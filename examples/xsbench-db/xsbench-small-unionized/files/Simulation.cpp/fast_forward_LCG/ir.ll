define internal fastcc noundef i64 @_Z16fast_forward_LCGmm(i64 noundef %seed, i64 noundef %n) unnamed_addr #6 !dbg !61 {
entry:
  %rem = urem i64 %n, -9223372036854775808, !dbg !62
  br label %while.cond, !dbg !63

while.cond:                                       ; preds = %if.end, %entry
  %n.addr.0 = phi i64 [ %rem, %entry ], [ %shr, %if.end ], !dbg !64
  %a.0 = phi i64 [ 2806196910506780709, %entry ], [ %mul4, %if.end ], !dbg !64
  %c.0 = phi i64 [ 1, %entry ], [ %mul3, %if.end ], !dbg !64
  %a_new.0 = phi i64 [ 1, %entry ], [ %a_new.1, %if.end ], !dbg !64
  %c_new.0 = phi i64 [ 0, %entry ], [ %c_new.1, %if.end ], !dbg !64
  %cmp = icmp ugt i64 %n.addr.0, 0, !dbg !65
  br i1 %cmp, label %while.body, label %while.end, !dbg !63

while.body:                                       ; preds = %while.cond
  %and = and i64 %n.addr.0, 1, !dbg !66
  %tobool = icmp ne i64 %and, 0, !dbg !67
  br i1 %tobool, label %if.then, label %if.end, !dbg !67

if.then:                                          ; preds = %while.body
  %mul = mul i64 %a_new.0, %a.0, !dbg !68
  %mul1 = mul i64 %c_new.0, %a.0, !dbg !69
  %add = add i64 %mul1, %c.0, !dbg !70
  br label %if.end, !dbg !71

if.end:                                           ; preds = %if.then, %while.body
  %a_new.1 = phi i64 [ %mul, %if.then ], [ %a_new.0, %while.body ], !dbg !64
  %c_new.1 = phi i64 [ %add, %if.then ], [ %c_new.0, %while.body ], !dbg !64
  %add2 = add i64 %a.0, 1, !dbg !72
  %mul3 = mul i64 %c.0, %add2, !dbg !73
  %mul4 = mul i64 %a.0, %a.0, !dbg !74
  %shr = lshr i64 %n.addr.0, 1, !dbg !75
  br label %while.cond, !dbg !63, !llvm.loop !76

while.end:                                        ; preds = %while.cond
  %mul5 = mul i64 %a_new.0, %seed, !dbg !78
  %add6 = add i64 %mul5, %c_new.0, !dbg !79
  %rem7 = urem i64 %add6, -9223372036854775808, !dbg !80
  ret i64 %rem7, !dbg !81
}
