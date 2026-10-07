"""Source as the device compilation saw it, line for line.

An application built with ``-grecord-command-line`` stores its compile command
in each compile unit of the debug info, and Proteus keeps it when it embeds the
device bitcode that Mneme records. Rerunning that command with ``-E`` for the
recorded GPU architecture resolves conditional compilation exactly as the
device compile did. Clang's line markers tie every preprocessed line back to
its original file and line, so the result is a *view* of each original file
with one entry per line:

  same       compiled as written
  expanded   compiled, with macros expanded (the expansion is kept)
  joined     part of a macro invocation expanded on an earlier line
  empty      compiled, but its macros expanded to nothing
  pragma     a ``#pragma`` the compiler saw
  directive  any other preprocessor directive
  skipped    removed by conditional compilation
  blank      empty in the original

The device source of a function is its original lines with directives and
skipped lines left blank, so line numbers from the debug info still apply.
Macros stay as written; ``expansions`` lists the ones the project defined.
"""

import hashlib
import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

from .ir import _parse_metadata

# Line kinds whose text is not part of the device source.
REMOVED = ("directive", "skipped")

_ESCAPE = re.compile(r"\\(\\|[0-9A-Fa-f]{2})")
_TARGET_CPU = re.compile(r'"target-cpu"="([^"]+)"')


@dataclass
class CompileUnit:
    """One compile unit of a recorded module and how to preprocess it again."""
    argv: List[str]
    # The compile's working directory and its main file, as an absolute path.
    directory: str
    file: str
    # The GPU architecture the module was compiled for, e.g. gfx942.
    arch: Optional[str]
    # MD5 of every file the debug info names, by absolute path.
    checksums: Dict[str, str] = field(default_factory=dict)

    @property
    def key(self) -> tuple:
        return tuple(self.argv), self.file, self.arch


def _llvm_string(value: str) -> str:
    """Decode a quoted metadata string. LLVM writes '"' as \\22, and '\\' as
    \\\\ (ROCm 6.4's LLVM 19) or \\5C."""
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return _ESCAPE.sub(lambda m: "\\" if m.group(1) == "\\" else chr(int(m.group(1), 16)), value)


def split_command(flags: str) -> List[str]:
    """Split a command line recorded by -grecord-command-line, which escapes
    spaces and backslashes in arguments with a backslash."""
    args, current, escaped, started = [], [], False, False
    for c in flags:
        if escaped:
            current.append(c)
            escaped = False
        elif c == "\\":
            escaped = started = True
        elif c == " ":
            if started:
                args.append("".join(current))
            current, started = [], False
        else:
            current.append(c)
            started = True
    if started:
        args.append("".join(current))
    return args


def _difile_path(fields: Dict[str, str]) -> Optional[str]:
    name = _llvm_string(fields.get("filename", '""'))
    directory = _llvm_string(fields.get("directory", '""'))
    if not name:
        return None
    return os.path.normpath(os.path.join(directory, name))


def compile_units(ir_text: str) -> List[CompileUnit]:
    """The compile units of a module that carry a recorded command line."""
    nodes = _parse_metadata(ir_text.splitlines())
    checksums = {}
    for kind, fields in nodes.values():
        if kind == "DIFile" and fields.get("checksumkind") == "CSK_MD5" and "checksum" in fields:
            path = _difile_path(fields)
            if path:
                checksums[path] = _llvm_string(fields["checksum"])
    cpu = _TARGET_CPU.search(ir_text)
    units = []
    for kind, fields in nodes.values():
        if kind != "DICompileUnit" or "flags" not in fields:
            continue
        argv = split_command(_llvm_string(fields["flags"]))
        file_ref = fields.get("file", "")
        file_node = nodes.get(int(file_ref[1:])) if file_ref[1:].isdigit() else None
        if not argv or not file_node:
            continue
        directory = _llvm_string(file_node[1].get("directory", '""'))
        path = _difile_path(file_node[1])
        arch = next((a.split("=", 1)[1] for a in reversed(argv) if a.startswith("-mcpu=")),
                    cpu.group(1) if cpu else None)
        units.append(CompileUnit(argv, directory, path, arch, checksums))
    return units


# The recorded command is rerun as it was, with options appended that the
# driver lets win over earlier ones: -E over -c and -S, the last -o, and
# --no-offload-arch=all over the recorded architectures. Only options that
# would still change what is printed, write a file, or fail without the
# build's plugins are removed, so nothing else about the command, such as
# which options take a value, needs to be known.
_DROP = {
    # Dependency lists and files.
    "-M", "-MM", "-MD", "-MMD", "-MP", "-MG", "-MV",
    # Output without line markers, with comments in macro expansions, with
    # only macros, or with nothing at all.
    "-P", "-CC", "-dM", "-dD", "-dI", "-dN", "-dE", "-###",
}
# -mcpu= is recorded for the device compile only; the host compile rejects it.
# The -M options here are the attached forms of _DROP_WITH_VALUE.
_DROP_PREFIXES = ("-mcpu=", "-fplugin=", "-fpass-plugin=", "-fplugin-arg-", "-mllvm=",
                  "-MF", "-MT", "-MQ", "-MJ")
# Removed together with the next argument, their value.
_DROP_WITH_VALUE = {"-MF", "-MT", "-MQ", "-MJ", "-mllvm"}
# -Xclang values that load plugins or pass LLVM options; the next -Xclang
# value belongs to them.
_XCLANG_PAIRS = {"-mllvm", "-load", "-plugin", "-add-plugin"}


def preprocess_argv(unit: CompileUnit, source: Optional[str] = None,
                    compiler: Optional[str] = None) -> List[str]:
    """The recorded command, changed to preprocess the unit's main file for its
    GPU architecture and write the result to stdout.

    ``source`` replaces the main file, e.g. with a copy of it; ``compiler``
    replaces the recorded compiler.
    """
    args = unit.argv[1:]
    out: List[str] = []
    found = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "-Xclang" and i + 1 < len(args):
            value = args[i + 1]
            if value in _XCLANG_PAIRS or value.startswith("-plugin-arg-"):
                i += 4 if i + 2 < len(args) and args[i + 2] == "-Xclang" else 2
                continue
        if a.startswith("-X") and "=" not in a and i + 1 < len(args):
            # -Xlinker, -Xarch_device and the like pass their value on; it is
            # not one of the driver's own options.
            out += args[i:i + 2]
            i += 2
            continue
        if a in _DROP_WITH_VALUE:
            i += 2
            continue
        if a in _DROP or a.startswith(_DROP_PREFIXES):
            i += 1
            continue
        if not a.startswith("-") and os.path.normpath(os.path.join(unit.directory, a)) == unit.file:
            # Replaced where it stands, so a -x before it still applies.
            found = True
            a = source or a
        out.append(a)
        i += 1
    if unit.arch:
        out += ["--no-offload-arch=all", f"--offload-arch={unit.arch}"]
    out += ["-E", "-C", "-dD", "--offload-device-only", "-Wno-unused-command-line-argument",
            "-o", "-"]
    if source:
        out += ["-iquote", os.path.dirname(unit.file)]
    if not found:
        out.append(source or unit.file)
    return [compiler or unit.argv[0]] + out


_MARKER = re.compile(r'^# (\d+) "((?:[^"\\]|\\.)*)"((?: \d+)*)\s*$')
_DIRECTIVE_ECHO = re.compile(r"^#\s*(define|undef)\s+([A-Za-z_]\w*)")


def _c_string(value: str) -> str:
    return re.sub(r"\\(.)", r"\1", value)


@dataclass
class _Output:
    """Preprocessed text of one file, by original line."""
    # Non-empty preprocessed text of each line.
    text: Dict[int, str] = field(default_factory=dict)
    # Lines with any trace in the output: text, an echoed #define or #undef,
    # a #pragma, or an #include that was entered.
    evidence: Set[int] = field(default_factory=set)
    system: bool = False


def parse_output(text: str, directory: str, rename: Optional[Dict[str, str]] = None
                 ) -> Tuple[Dict[str, _Output], Dict[str, str]]:
    """Split ``clang -E -C -dD`` output by original file and line.

    Returns the output of each file, by absolute path, and the file that last
    defined each macro (``<command line>`` and ``<built-in>`` for those).
    """
    files: Dict[str, _Output] = {}
    macros: Dict[str, str] = {}
    rename = rename or {}
    cur: Optional[_Output] = None
    cur_path, line = None, 0
    for raw in text.split("\n"):
        m = _MARKER.match(raw)
        if m:
            name = _c_string(m.group(2))
            flags = m.group(3).split()
            path = name if name.startswith("<") else os.path.normpath(os.path.join(directory, name))
            path = rename.get(path, path)
            if "2" in flags:
                # Back from an include: the #include line was the one before.
                files.setdefault(path, _Output()).evidence.add(int(m.group(1)) - 1)
            cur_path, line = path, int(m.group(1))
            cur = files.setdefault(path, _Output())
            if "3" in flags:
                cur.system = True
            continue
        if cur is None:
            continue
        d = _DIRECTIVE_ECHO.match(raw)
        if d:
            if d.group(1) == "define":
                macros[d.group(2)] = cur_path
            else:
                macros.pop(d.group(2), None)
            cur.evidence.add(line)
        elif raw.strip():
            cur.text[line] = raw
            cur.evidence.add(line)
        line += 1
    return files, macros


_LINE_DIRECTIVE = re.compile(r"^[ \t]*#[ \t]*(line\b|\d)", re.M)
_CONDITIONAL = re.compile(r"^\s*#\s*(if|ifdef|ifndef|elif|elifdef|elifndef|else|endif)\b")
_DIRECTIVE = re.compile(r"^\s*#")
_PRAGMA = re.compile(r"^\s*#\s*pragma\b")


def _directive_lines(lines: List[str]) -> Tuple[Set[int], Dict[int, str]]:
    """Line numbers of preprocessor directives, including continuation lines,
    and the conditional keyword on each conditional directive's first line.
    Lines inside block comments are not directives."""
    directives: Set[int] = set()
    conditionals: Dict[int, str] = {}
    in_comment, continued = False, False
    for n, text in enumerate(lines, 1):
        if continued:
            directives.add(n)
            continued = text.rstrip("\r\n").endswith("\\")
            continue
        if not in_comment and _DIRECTIVE.match(text):
            directives.add(n)
            m = _CONDITIONAL.match(text)
            if m:
                conditionals[n] = m.group(1)
            continued = text.rstrip("\r\n").endswith("\\")
            continue
        in_comment = _ends_in_comment(text, in_comment)
    return directives, conditionals


def _ends_in_comment(text: str, in_comment: bool) -> bool:
    """Whether a block comment is still open at the end of the line."""
    state = [in_comment]
    for _ in _lex_line(text, state):
        pass
    return state[0]


def _live_lines(lines: List[str], conditionals: Dict[int, str], evidence: Set[int]) -> List[bool]:
    """Whether each line is in a taken branch of every conditional around it.

    A branch was taken if anything inside it left a trace in the output. A
    branch without any trace could only hold blank lines, comments outside
    the ``-C`` output, or macros that expand to nothing; it is treated as not
    taken, which changes no generated code.
    """
    n_lines = len(lines)
    live = [True] * (n_lines + 1)
    # Each open group: the branches so far, as [start line, end line].
    stack: List[List[List[int]]] = []
    branches: List[List[int]] = []
    for n in range(1, n_lines + 1):
        kind = conditionals.get(n)
        if kind in ("if", "ifdef", "ifndef"):
            stack.append([[n + 1, n_lines]])
        elif kind in ("elif", "elifdef", "elifndef", "else") and stack:
            stack[-1][-1][1] = n - 1
            stack[-1].append([n + 1, n_lines])
        elif kind == "endif" and stack:
            stack[-1][-1][1] = n - 1
            branches += stack.pop()
    for group in stack:  # unterminated; the compile would have failed
        branches += group
    for start, end in branches:
        if not any(start <= e <= end for e in evidence):
            for k in range(start, end + 1):
                live[k] = False
    return live[1:]


@dataclass
class FileView:
    """One original file as a device compilation preprocessed it."""
    path: str
    lines: List[str]
    kinds: List[str]
    expanded: Dict[int, str]
    # Macros used on each expanded line, by origin: project, cmdline, system, builtin.
    used: Dict[int, Dict[str, List[str]]]

    def kind(self, line: int) -> str:
        return self.kinds[line - 1]

    def text(self, start: int, end: int) -> str:
        """Lines ``start`` to ``end`` with directives and skipped lines blank."""
        out = []
        for n in range(start, min(end, len(self.lines)) + 1):
            text = self.lines[n - 1]
            if self.kinds[n - 1] in REMOVED:
                text = "\r\n" if text.endswith("\r\n") else ("\n" if text.endswith("\n") else "")
            out.append(text)
        return "".join(out)

    def function_end(self, start: int, last_code_line: Optional[int] = None) -> Optional[int]:
        """The line of the closing brace of the function that starts on
        ``start``, counting only what the device compiled."""
        code: List[Optional[str]] = []
        for n, (text, kind) in enumerate(zip(self.lines, self.kinds), 1):
            if kind in REMOVED or kind in ("joined", "pragma"):
                code.append(None)
            elif kind == "expanded":
                code.append(self.expanded[n])
            else:
                code.append(text)
        return function_end(code, start, last_code_line)

    def contradiction(self, lines: Iterable[int]) -> Optional[int]:
        """The first of ``lines``, which the debug info attributes code to, that
        the view says was not compiled. There is none unless the view is wrong,
        e.g. because the file was preprocessed with other options or headers
        than the build used."""
        for n in sorted(set(lines)):
            if n > len(self.kinds) or (n > 0 and self.kinds[n - 1] in REMOVED + ("blank",)):
                return n
        return None

    def expansions(self, start: int, end: int) -> List[dict]:
        """Expanded lines in ``start``..``end`` that use the project's own or
        command-line macros."""
        out = []
        for n in range(start, min(end, len(self.lines)) + 1):
            used = self.used.get(n, {})
            names = [name for origin in ("project", "cmdline") for name in used.get(origin, [])]
            if names:
                out.append({"line": n, "macros": names, "text": self.expanded[n].strip()})
        return out


_IDENT = re.compile(r"[A-Za-z_]\w*")


def build_view(path: str, source: str, output: _Output, macros: Dict[str, str],
               files: Dict[str, _Output]) -> FileView:
    lines = source.splitlines(keepends=True)
    directives, conditionals = _directive_lines(lines)
    live = _live_lines(lines, conditionals, output.evidence)
    kinds: List[str] = []
    used: Dict[int, Dict[str, List[str]]] = {}
    open_parens = 0
    for n, text in enumerate(lines, 1):
        out = output.text.get(n)
        if not live[n - 1]:
            kind = "skipped"
        elif n in directives:
            kind = "pragma" if _PRAGMA.match(text) and out is not None else "directive"
        elif not text.strip():
            kind = "blank"
        elif out is None:
            kind = "joined" if open_parens > 0 else "empty"
        elif _squash(out) == _squash(text):
            kind = "same"
        else:
            kind = "expanded"
        if kind in ("same", "expanded", "empty"):
            open_parens = _paren_balance(text)
        elif kind == "joined":
            open_parens += _paren_balance(text)
        elif kind != "blank":
            open_parens = 0
        if kind == "expanded":
            used[n] = _macros_used(text, macros, files)
        kinds.append(kind)
    expanded = {n: output.text[n] for n, k in enumerate(kinds, 1) if k == "expanded"}
    return FileView(path, lines, kinds, expanded, used)


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _paren_balance(text: str) -> int:
    balance = 0
    for kind, c in _lex_line(text, [False]):
        if kind == "code":
            balance += {"(": 1, ")": -1}.get(c, 0)
    return balance


def _macros_used(text: str, macros: Dict[str, str], files: Dict[str, _Output]) -> Dict[str, List[str]]:
    used: Dict[str, List[str]] = {}
    code = "".join(c if kind == "code" else " " for kind, c in _lex_line(text, [False], True))
    for name in _IDENT.findall(code):
        where = macros.get(name)
        if where is None:
            continue
        if where == "<command line>":
            origin = "cmdline"
        elif where.startswith("<"):
            origin = "builtin"
        elif files.get(where) and files[where].system:
            origin = "system"
        else:
            origin = "project"
        names = used.setdefault(origin, [])
        if name not in names:
            names.append(name)
    return used


def _lex_line(text: str, state: List[bool], spaces: bool = False) -> Iterator[Tuple[str, str]]:
    """Yield ("code", char) for characters outside comments and literals, and
    ("literal", "x") once per string or character literal; with ``spaces``,
    also ("space", " ") for whitespace and comments. ``state[0]`` says
    whether a block comment is open, and is updated."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if state[0]:
            end = text.find("*/", i)
            if end < 0:
                return
            state[0] = False
            i = end + 2
            if spaces:
                yield "space", " "
            continue
        if text.startswith("//", i):
            return
        if text.startswith("/*", i):
            state[0] = True
            i += 2
            continue
        if c == '"' or (c == "'" and not _digit_separator(text, i)):
            raw = c == '"' and i > 0 and text[i - 1] == "R"
            if raw:
                m = re.match(r'"([^()\\ ]{0,16})\(', text[i:])
                end = text.find(")" + m.group(1) + '"', i) if m else -1
                i = end + len(m.group(1)) + 2 if end >= 0 else n
            else:
                j = i + 1
                while j < n and text[j] != c:
                    j += 2 if text[j] == "\\" else 1
                i = j + 1
            yield "literal", "x"
            continue
        if not c.isspace():
            yield "code", c
        elif spaces:
            yield "space", " "
        i += 1


def _digit_separator(text: str, i: int) -> bool:
    """A ' inside a number, as in 1'000'000."""
    j = i
    while j > 0 and (text[j - 1].isalnum() or text[j - 1] in "._"):
        j -= 1
    return j < i and text[j].isdigit() and i + 1 < len(text) and text[i + 1].isalnum()


def _significant(code: List[Optional[str]], start: int) -> Iterator[Tuple[int, str]]:
    state = [False]
    for n in range(start, len(code) + 1):
        text = code[n - 1]
        if text is None:
            continue
        for kind, c in _lex_line(text, state):
            yield n, c


# Words after which a '{' opens a lambda's body even inside parentheses.
_BODY_AFTER_WORD = {"mutable", "noexcept", "const", "constexpr", "consteval"}


def function_end(code: List[Optional[str]], start: int,
                 last_code_line: Optional[int] = None) -> Optional[int]:
    """Find the line of the brace that closes the function starting on line
    ``start``. ``code[n - 1]`` is line n's text, or None to ignore the line.

    Braced initializers before the body, such as default arguments, are
    skipped, and a constructor's member initializers (``: a{1}, b{2} {``) do
    not end the function. Returns None when no body is found, or when it would
    end before ``last_code_line``.
    """
    tokens = list(_significant(code, start))
    depth, init_depth, opened, member_init = 0, 0, False, False
    paren, arrow = 0, False
    prev, before_word = "", ""
    word: List[str] = []
    for i, (n, c) in enumerate(tokens):
        if not opened:
            if c == "{":
                after_word = bool(word) or prev == ">"
                body = not init_depth and (
                    prev in (")", "]")
                    # Outside the parameters: const, noexcept, override, a
                    # trailing return type or a member initializer.
                    or (after_word and (paren <= 0 or arrow or "".join(word) in _BODY_AFTER_WORD)))
                if body:
                    opened, depth = True, 1
                    # name{...} after ':' or ',' initializes a member.
                    member_init = bool(word) and before_word in (":", ",")
                else:
                    init_depth += 1
            elif c == "}" and init_depth:
                init_depth -= 1
            elif c == "(":
                paren, arrow = paren + 1, False
            elif c == ")":
                paren -= 1
            elif c == ">" and prev == "-":
                arrow = True
            elif c in ",;":
                arrow = False
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                after = tokens[i + 1][1] if i + 1 < len(tokens) else ""
                if member_init and after in (",", "{"):
                    # A member initializer; the body is still to come.
                    opened = False
                else:
                    if last_code_line and n < last_code_line:
                        return None
                    return n
        if c.isalnum() or c == "_":
            if not word:
                before_word = prev
            word.append(c)
        else:
            word = []
        prev = c
        if len(tokens) > 200000:
            break
    return None


def md5(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return None


@dataclass
class UnitViews:
    """Views of the files of one compile unit, or why there are none."""
    views: Dict[str, FileView] = field(default_factory=dict)
    error: Optional[str] = None
    # Set when the main file was preprocessed from Mneme's copy.
    used_copy: bool = False
    # Set when the recorded compiler was missing and another one was used.
    compiler: Optional[str] = None


def preprocess(unit: CompileUnit, wanted: Set[str], copies: Optional[Dict[str, str]] = None,
               fallback_compiler: Optional[str] = None, timeout: int = 600) -> UnitViews:
    """Preprocess ``unit`` again and build views of the files in ``wanted``
    whose contents still match the debug info's checksums.

    When the main file changed or moved since the build, Mneme's copy of it
    (from ``copies``) is preprocessed instead if its checksum matches.
    """
    source = None
    expected = unit.checksums.get(unit.file)
    if expected and md5(unit.file) != expected:
        copy = (copies or {}).get(unit.file)
        if not copy or md5(copy) != expected:
            return UnitViews(error=f"{unit.file} changed since it was compiled")
        source = copy
    if not os.path.isdir(unit.directory):
        return UnitViews(error=f"compile directory {unit.directory} is gone")
    compiler = None
    if not os.path.isfile(unit.argv[0]) and fallback_compiler:
        compiler = fallback_compiler
    argv = preprocess_argv(unit, source, compiler)
    try:
        res = subprocess.run(argv, cwd=unit.directory, capture_output=True, text=True,
                             timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return UnitViews(error=f"could not run {argv[0]}: {e}")
    if res.returncode:
        last = res.stderr.strip().splitlines()[-1:] or [""]
        return UnitViews(error=f"{argv[0]} failed: {last[0]}")
    rename = {os.path.normpath(source): unit.file} if source else {}
    files, macros = parse_output(res.stdout, unit.directory, rename)
    result = UnitViews(used_copy=bool(source), compiler=compiler)
    for path in wanted:
        output = files.get(path)
        if output is None:
            continue
        read_from = source if source and path == unit.file else path
        expected = unit.checksums.get(path)
        if expected and md5(read_from) != expected:
            continue
        try:
            with open(read_from, newline="") as f:
                text = f.read()
        except OSError:
            continue
        if _LINE_DIRECTIVE.search(text):
            # The debug info's line numbers follow #line, not the file.
            continue
        result.views[path] = build_view(path, text, output, macros, files)
    return result
