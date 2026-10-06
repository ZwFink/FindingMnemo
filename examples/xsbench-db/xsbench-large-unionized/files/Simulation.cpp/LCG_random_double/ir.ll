define internal fastcc noundef double @_Z17LCG_random_doublePm(ptr noundef %seed) unnamed_addr #6 !dbg !82 {
entry:
  %0 = load i64, ptr %seed, align 8, !dbg !83, !tbaa !22
  %mul = mul i64 2806196910506780709, %0, !dbg !84
  %add = add i64 %mul, 1, !dbg !85
  %rem = urem i64 %add, -9223372036854775808, !dbg !86
  store i64 %rem, ptr %seed, align 8, !dbg !87, !tbaa !22
  %conv = uitofp i64 %rem to double, !dbg !88
  %div = fdiv contract double %conv, 0x43E0000000000000, !dbg !89
  ret double %div, !dbg !90
}
