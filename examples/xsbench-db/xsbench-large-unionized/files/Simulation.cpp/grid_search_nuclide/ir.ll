define internal fastcc noundef i64 @_Z19grid_search_nuclideldP16NuclideGridPointll(i64 noundef %n, double noundef %quarry, ptr noundef %A, i64 noundef %low, i64 noundef %high) unnamed_addr #6 !dbg !333 {
entry:
  %sub = sub nsw i64 %high, %low, !dbg !334
  br label %while.cond, !dbg !335

while.cond:                                       ; preds = %if.end, %entry
  %lowerLimit.0 = phi i64 [ %low, %entry ], [ %lowerLimit.1, %if.end ], !dbg !336
  %upperLimit.0 = phi i64 [ %high, %entry ], [ %upperLimit.1, %if.end ], !dbg !337
  %length.0 = phi i64 [ %sub, %entry ], [ %sub2, %if.end ], !dbg !337
  %cmp = icmp sgt i64 %length.0, 1, !dbg !338
  br i1 %cmp, label %while.body, label %while.end, !dbg !335

while.body:                                       ; preds = %while.cond
  %div = sdiv i64 %length.0, 2, !dbg !339
  %add = add nsw i64 %lowerLimit.0, %div, !dbg !340
  %arrayidx = getelementptr inbounds %struct.NuclideGridPoint, ptr %A, i64 %add, !dbg !341
  %0 = load double, ptr %arrayidx, align 8, !dbg !342, !tbaa !262
  %cmp1 = fcmp contract ogt double %0, %quarry, !dbg !343
  br i1 %cmp1, label %if.then, label %if.else, !dbg !341

if.then:                                          ; preds = %while.body
  br label %if.end, !dbg !344

if.else:                                          ; preds = %while.body
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  %lowerLimit.1 = phi i64 [ %lowerLimit.0, %if.then ], [ %add, %if.else ], !dbg !337
  %upperLimit.1 = phi i64 [ %add, %if.then ], [ %upperLimit.0, %if.else ], !dbg !337
  %sub2 = sub nsw i64 %upperLimit.1, %lowerLimit.1, !dbg !345
  br label %while.cond, !dbg !335, !llvm.loop !346

while.end:                                        ; preds = %while.cond
  ret i64 %lowerLimit.0, !dbg !348
}
