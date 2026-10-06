define internal fastcc noundef i64 @_Z11grid_searchldPd(i64 noundef %n, double noundef %quarry, ptr noalias noundef %A) unnamed_addr #6 !dbg !193 {
entry:
  %sub = sub nsw i64 %n, 1, !dbg !194
  br label %while.cond, !dbg !195

while.cond:                                       ; preds = %if.end, %entry
  %lowerLimit.0 = phi i64 [ 0, %entry ], [ %lowerLimit.1, %if.end ], !dbg !196
  %upperLimit.0 = phi i64 [ %sub, %entry ], [ %upperLimit.1, %if.end ], !dbg !197
  %length.0 = phi i64 [ %sub, %entry ], [ %sub3, %if.end ], !dbg !197
  %cmp = icmp sgt i64 %length.0, 1, !dbg !198
  br i1 %cmp, label %while.body, label %while.end, !dbg !195

while.body:                                       ; preds = %while.cond
  %div = sdiv i64 %length.0, 2, !dbg !199
  %add = add nsw i64 %lowerLimit.0, %div, !dbg !200
  %arrayidx = getelementptr inbounds double, ptr %A, i64 %add, !dbg !201
  %0 = load double, ptr %arrayidx, align 8, !dbg !201, !tbaa !46
  %cmp2 = fcmp contract ogt double %0, %quarry, !dbg !202
  br i1 %cmp2, label %if.then, label %if.else, !dbg !201

if.then:                                          ; preds = %while.body
  br label %if.end, !dbg !203

if.else:                                          ; preds = %while.body
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  %lowerLimit.1 = phi i64 [ %lowerLimit.0, %if.then ], [ %add, %if.else ], !dbg !197
  %upperLimit.1 = phi i64 [ %add, %if.then ], [ %upperLimit.0, %if.else ], !dbg !197
  %sub3 = sub nsw i64 %upperLimit.1, %lowerLimit.1, !dbg !204
  br label %while.cond, !dbg !195, !llvm.loop !205

while.end:                                        ; preds = %while.cond
  ret i64 %lowerLimit.0, !dbg !207
}
