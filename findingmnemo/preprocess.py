"""Source as the device compilation saw it, line for line.

An application built with ``-grecord-command-line`` stores its compile command
in each compile unit of the debug info, and Proteus keeps it when it embeds the
device bitcode that Mneme records. Rerunning that command with ``-E
-fdirectives-only`` for the recorded GPU architecture resolves ``#include``s
and conditional compilation exactly as the device compile did, but leaves
macros as written. Clang's line markers tie every printed line back to its
original file and line, so a line was compiled if it was printed.

The device source of a function is its original lines with directives and the
lines conditional compilation removed left blank, so line numbers from the
debug info still apply. Clang prints code again token by token, changing its
whitespace, so the text comes from the original file.
"""

import hashlib
import os
import re
import subprocess
from dataclasses import dataclass, field
from functools import cached_property
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

from .ir import _parse_metadata

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
    # Metadata id of the DICompileUnit in its module.
    id: Optional[int] = None

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
    for ref, (kind, fields) in nodes.items():
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
        units.append(CompileUnit(argv, directory, path, arch, checksums, ref))
    return units


# The recorded command is rerun as it was, with options appended that the
# driver lets win over earlier ones: -E over -c and -S, the last -o, and
# --no-offload-arch=all over the recorded architectures. Only options that
# would still change what is printed, write a file, or fail without the
# build's plugins are removed, so nothing else about the command, such as
# which options take a value, needs to be known.
_DROP = {
    # Dependency lists instead of the source, and dependency files. -MG is an
    # error without -M or -MM. The options that only modify these (-MF, -MT,
    # -MQ, -MP, -MV) do nothing once they are gone.
    "-M", "-MM", "-MD", "-MMD", "-MG",
    # Output without line markers, with only macros, or with nothing at all.
    "-P", "-dM", "-###",
}
# -mcpu= is recorded for the device compile only; the host compile rejects it.
# A frontend plugin is loaded even to preprocess, and fails if it moved; pass
# plugins are not loaded. -MJ writes a compilation database entry.
_DROP_PREFIXES = ("-mcpu=", "-fplugin=", "-fplugin-arg-", "-mllvm=", "-MJ")
# Removed together with the next argument, their value. Without its plugin,
# a plugin's -mllvm options are unknown, and which ones are its cannot be told.
_DROP_WITH_VALUE = {"-MJ", "-mllvm"}
# -Xclang values that load plugins or pass LLVM options; the next -Xclang
# value belongs to them.
_XCLANG_PAIRS = {"-mllvm", "-load", "-plugin", "-add-plugin"}


def preprocess_argv(unit: CompileUnit, expand_macros: bool = False) -> List[str]:
    """The recorded command, changed to preprocess the unit's main file for its
    GPU architecture and write the result to stdout.

    Only directives are processed, and comments are kept, unless
    ``expand_macros``.
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
            found = True
        out.append(a)
        i += 1
    if unit.arch:
        out += ["--no-offload-arch=all", f"--offload-arch={unit.arch}"]
    out += ["-E"] + ([] if expand_macros else ["-C", "-fdirectives-only"])
    out += ["--offload-device-only", "-Wno-unused-command-line-argument", "-o", "-"]
    if not found:
        out.append(unit.file)
    return [unit.argv[0]] + out


_MARKER = re.compile(r'^# (\d+) "((?:[^"\\]|\\.)*)"((?: \d+)*)\s*$')
_LINE_DIRECTIVE = re.compile(r"^[ \t]*#[ \t]*(line\b|\d)", re.M)
_DIRECTIVE = re.compile(r"^\s*#")
_PRAGMA = re.compile(r"^\s*#\s*pragma\b")
# Clang ends lines only at \n, \r\n or \r, unlike str.splitlines, which also
# ends them at a form feed and other characters.
_SOURCE_LINE = re.compile(r"[^\r\n]*(?:\r\n?|\n)|[^\r\n]+\Z")


def _c_string(value: str) -> str:
    return re.sub(r"\\(.)", r"\1", value)


def parse_output(text: str, directory: str) -> Dict[str, Dict[int, str]]:
    """Split ``clang -E`` output into the non-empty text of each original
    file's lines, by the file's absolute path."""
    files: Dict[str, Dict[int, str]] = {}
    cur: Optional[Dict[int, str]] = None
    line = 0
    for raw in text.split("\n"):
        m = _MARKER.match(raw)
        if m:
            name = _c_string(m.group(2))
            path = name if name.startswith("<") else os.path.normpath(os.path.join(directory, name))
            cur = files.setdefault(path, {})
            line = int(m.group(1))
            continue
        if cur is None:
            continue
        if raw.strip():
            cur[line] = raw
        line += 1
    return files


@dataclass
class FileView:
    """One original file as a device compilation preprocessed it."""
    path: str
    lines: List[str]
    # Whether the device compile kept each line: code, comments and #pragmas
    # in the branches it took, but no other directive.
    kept: List[bool]
    # The code on each line with macros expanded, which can hide braces.
    code: Dict[int, str]

    def compiled(self, line: int) -> bool:
        return 0 < line <= len(self.kept) and self.kept[line - 1]

    def text(self, start: int, end: int) -> str:
        """Lines ``start`` to ``end``, with the ones not kept blank. Lines with
        only whitespace stay as they are."""
        out = []
        for n in range(start, min(end, len(self.lines)) + 1):
            text = self.lines[n - 1]
            if not self.kept[n - 1] and text.strip():
                text = text[len(text.rstrip("\r\n")):]
            out.append(text)
        return "".join(out)

    def function_column(self, start: int, name: str, is_lambda: bool) -> Optional[int]:
        """Where on line ``start`` the function begins, as in the code the
        device compiled; see ``function_column``."""
        text = self.code.get(start)
        return function_column(text, name, is_lambda) if text else None

    def function_end(self, start: int, last_code_line: Optional[int] = None,
                     column: int = 0) -> Optional[int]:
        """The line of the closing brace of the function that starts at
        ``column`` of line ``start``, counting only what the device compiled."""
        return function_end(self._code_lines, start, last_code_line, column)

    @cached_property
    def _code_lines(self) -> List[Optional[str]]:
        return [self.code.get(n) for n in range(1, len(self.lines) + 1)]

    def contradiction(self, lines: Iterable[int]) -> Optional[int]:
        """The first of ``lines``, which the debug info attributes code to, that
        the view says was not compiled. There is none unless the view is wrong,
        e.g. because the file was preprocessed with other options or headers
        than the build used."""
        for n in sorted(set(lines)):
            # Line 0 is code the compiler made up.
            if n and not self.compiled(n):
                return n
        return None


def build_view(path: str, source: str, printed: Dict[int, str], expanded: Dict[int, str]
               ) -> FileView:
    """The view of a file from its lines as printed with only directives
    processed, and with macros expanded."""
    lines = _SOURCE_LINE.findall(source)
    kept: List[bool] = []
    in_comment = [False]
    for n, text in enumerate(lines, 1):
        out = printed.get(n)
        if out is None:
            # Code continued with a backslash, which may have spaces after it,
            # is printed on its first line.
            kept.append(n > 1 and kept[-1] and lines[n - 2].rstrip(" \t\f\v\r\n").endswith("\\"))
            continue
        directive = not in_comment[0] and _DIRECTIVE.match(out) and not _PRAGMA.match(out)
        kept.append(not directive)
        for _ in _lex_line(out, in_comment):
            pass
    code = {n: text for n, text in expanded.items() if not _DIRECTIVE.match(text)}
    return FileView(path, lines, kept, code)


def _lex_line(text: str, state: List[bool]) -> Iterator[Tuple[str, str, int]]:
    """Yield ("code", char, index) for characters outside comments and
    literals, and ("literal", "x", index) once per string or character literal,
    at its start. ``state[0]`` says whether a block comment is open, and is
    updated."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if state[0]:
            end = text.find("*/", i)
            if end < 0:
                return
            state[0] = False
            i = end + 2
            continue
        if text.startswith("//", i):
            return
        if text.startswith("/*", i):
            state[0] = True
            i += 2
            continue
        if c == '"' or (c == "'" and not _digit_separator(text, i)):
            start = i
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
            yield "literal", "x", start
            continue
        if not c.isspace():
            yield "code", c, i
        i += 1


def _digit_separator(text: str, i: int) -> bool:
    """A ' inside a number, as in 1'000'000."""
    j = i
    while j > 0 and (text[j - 1].isalnum() or text[j - 1] in "._"):
        j -= 1
    return j < i and text[j].isdigit() and i + 1 < len(text) and text[i + 1].isalnum()


def _significant(code: List[Optional[str]], start: int, column: int = 0
                 ) -> Iterator[Tuple[int, str]]:
    state = [False]
    for n in range(start, len(code) + 1):
        text = code[n - 1]
        if text is None:
            continue
        for _, c, i in _lex_line(text, state):
            if n > start or i >= column:
                yield n, c


def function_column(text: str, name: str, is_lambda: bool) -> Optional[int]:
    """Where the function begins on ``text``, the line the debug info starts
    it on: at its name, or at a lambda's ``[``. Code before it on the line,
    such as an ``if`` the lambda is written in, is not part of the function.

    None if the name is not on the line, or the line does not start exactly
    one lambda.
    """
    # Comments become spaces and each literal an x.
    chars = [" "] * len(text)
    for _, c, i in _lex_line(text, [False]):
        chars[i] = c
    code = "".join(chars)
    if is_lambda:
        starts = [i for i, c in enumerate(code) if c == "[" and _introduces_lambda(code, i)]
        return starts[0] if len(starts) == 1 else None
    if name.startswith("operator"):
        m = re.search(r"\boperator\b", code)
        return m.start() if m else None
    if name.startswith("~"):
        pattern = r"~\s*" + re.escape(name[1:].split("<")[0]) + r"\b"
    else:
        pattern = r"\b" + re.escape(name.split("<")[0]) + r"\b"
    for m in re.finditer(pattern, code):
        # The name of the function, not of the class in Box<T>::Box( or of a
        # struct the line also opens.
        rest = code[_after_template_args(code, m.end()):].lstrip()
        if not rest or rest.startswith("("):
            return m.start()
    return None


def _introduces_lambda(code: str, i: int) -> bool:
    """Whether the ``[`` at ``i`` starts a lambda, not a subscript or an
    attribute's [[."""
    before = code[:i].rstrip()
    if code.startswith("[", i + 1) or before.endswith("["):
        return False
    return not before or not (before[-1].isalnum() or before[-1] in "_)]")


def _after_template_args(code: str, i: int) -> int:
    """The index after the template arguments that start at ``i``, if any."""
    j = len(code) - len(code[i:].lstrip())
    if not code.startswith("<", j):
        return i
    depth = 0
    for k in range(j, len(code)):
        depth += {"<": 1, ">": -1}.get(code[k], 0)
        if depth == 0:
            return k + 1
    return len(code)


# Words after which a '{' opens a lambda's body even inside parentheses.
_BODY_AFTER_WORD = {"mutable", "noexcept", "const", "constexpr", "consteval"}


def function_end(code: List[Optional[str]], start: int,
                 last_code_line: Optional[int] = None, column: int = 0) -> Optional[int]:
    """Find the line of the brace that closes the function starting at
    ``column`` of line ``start``. ``code[n - 1]`` is line n's text, or None to
    ignore the line.

    Braced initializers before the body, such as default arguments, are
    skipped, and a constructor's member initializers (``: a{1}, b{2} {``) do
    not end the function. Returns None when no body is found, or when it would
    end before ``last_code_line``.
    """
    depth, init_depth, opened, member_init = 0, 0, False, False
    paren, arrow = 0, False
    prev, before_word = "", ""
    word: List[str] = []
    for (n, c), after in _with_next(_significant(code, start, column)):
        if not opened:
            if c == "{":
                after_word = bool(word) or prev == ">"
                body = not init_depth and (
                    prev in (")", "]")
                    # After the last member initializer, as in : a{1} {
                    or (prev == "}" and member_init)
                    # After a ref-qualifier (const& {, && {) or a trailing
                    # return type of pointer or reference (-> int* {).
                    or (prev in ("&", "*") and paren <= 0)
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
            elif c == ";" and not init_depth and paren <= 0:
                # A declaration without a body. A defaulted or deleted
                # function ends here; anything else, such as the forward
                # declaration an implicit member points to, has no body.
                if before_word == "=" and "".join(word) in ("default", "delete"):
                    return None if last_code_line and n < last_code_line else n
                return None
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
    return None


def _with_next(tokens: Iterator[Tuple[int, str]]) -> Iterator[Tuple[Tuple[int, str], str]]:
    """Each token with the character after it, or "" after the last."""
    current = next(tokens, None)
    for token in tokens:
        yield current, token[1]
        current = token
    if current:
        yield current, ""


def md5(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return None


class PreprocessError(Exception):
    """The files of a compile unit cannot be preprocessed the way the build did."""


def preprocess(unit: CompileUnit, wanted: Set[str], timeout: int = 600) -> Dict[str, FileView]:
    """Preprocess ``unit`` again and build views of the files in ``wanted``
    that it includes.

    Raises PreprocessError if the main file or a file in ``wanted`` changed
    since the build, if the recorded compile cannot be rerun, or if a file
    cannot be lined up with the debug info.
    """
    for path in sorted({unit.file} | wanted):
        expected = unit.checksums.get(path)
        if expected and md5(path) != expected:
            raise PreprocessError(f"{path} changed since it was compiled")
    if not os.path.isdir(unit.directory):
        raise PreprocessError(f"the compile directory of {unit.file}, {unit.directory}, is gone")
    outputs = []
    for expand_macros in (False, True):
        argv = preprocess_argv(unit, expand_macros)
        try:
            res = subprocess.run(argv, cwd=unit.directory, capture_output=True, text=True,
                                 timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise PreprocessError(f"could not run {argv[0]} to preprocess {unit.file}: {e}")
        if res.returncode:
            last = res.stderr.strip().splitlines()[-1:] or [""]
            raise PreprocessError(f"{argv[0]} failed to preprocess {unit.file}: {last[0]}")
        outputs.append(parse_output(res.stdout, unit.directory))
    printed, expanded = outputs
    views = {}
    for path in wanted:
        if path not in printed:
            continue
        try:
            with open(path, newline="") as f:
                text = f.read()
        except OSError as e:
            raise PreprocessError(f"cannot read {path}: {e}")
        if _LINE_DIRECTIVE.search(text):
            raise PreprocessError(f"{path} has #line directives, so the debug info's line "
                                  f"numbers do not refer to its lines")
        views[path] = build_view(path, text, printed[path], expanded.get(path, {}))
    return views
