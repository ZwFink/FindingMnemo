define internal fastcc noundef i32 @_Z8pick_matPm(ptr noundef %seed) unnamed_addr #6 !dbg !91 {
entry:
  %dist = alloca [12 x double], align 16, addrspace(5)
  %dist.ascast = addrspacecast ptr addrspace(5) %dist to ptr
  call void @llvm.lifetime.start.p5(i64 96, ptr addrspace(5) %dist) #9, !dbg !92
  call void @llvm.memset.p0.i64(ptr align 16 %dist.ascast, i8 0, i64 96, i1 false), !dbg !93, !annotation !94
  store double 1.400000e-01, ptr %dist.ascast, align 16, !dbg !95, !tbaa !46
  %arrayidx1 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 1, !dbg !96
  store double 5.200000e-02, ptr %arrayidx1, align 8, !dbg !97, !tbaa !46
  %arrayidx2 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 2, !dbg !98
  store double 2.750000e-01, ptr %arrayidx2, align 16, !dbg !99, !tbaa !46
  %arrayidx3 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 3, !dbg !100
  store double 1.340000e-01, ptr %arrayidx3, align 8, !dbg !101, !tbaa !46
  %arrayidx4 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 4, !dbg !102
  store double 1.540000e-01, ptr %arrayidx4, align 16, !dbg !103, !tbaa !46
  %arrayidx5 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 5, !dbg !104
  store double 6.400000e-02, ptr %arrayidx5, align 8, !dbg !105, !tbaa !46
  %arrayidx6 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 6, !dbg !106
  store double 6.600000e-02, ptr %arrayidx6, align 16, !dbg !107, !tbaa !46
  %arrayidx7 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 7, !dbg !108
  store double 5.500000e-02, ptr %arrayidx7, align 8, !dbg !109, !tbaa !46
  %arrayidx8 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 8, !dbg !110
  store double 8.000000e-03, ptr %arrayidx8, align 16, !dbg !111, !tbaa !46
  %arrayidx9 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 9, !dbg !112
  store double 1.500000e-02, ptr %arrayidx9, align 8, !dbg !113, !tbaa !46
  %arrayidx10 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 10, !dbg !114
  store double 2.500000e-02, ptr %arrayidx10, align 16, !dbg !115, !tbaa !46
  %arrayidx11 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 11, !dbg !116
  store double 1.300000e-02, ptr %arrayidx11, align 8, !dbg !117, !tbaa !46
  %call = call contract fastcc noundef double @_Z17LCG_random_doublePm(ptr noundef %seed) #8, !dbg !118
  br label %for.cond, !dbg !119

for.cond:                                         ; preds = %for.inc18, %entry
  %retval.0 = phi i32 [ undef, %entry ], [ %retval.1, %for.inc18 ]
  %i.0 = phi i32 [ 0, %entry ], [ %inc, %for.inc18 ], !dbg !120
  %cmp = icmp slt i32 %i.0, 12, !dbg !121
  br i1 %cmp, label %for.body, label %for.cond.cleanup, !dbg !122

for.cond.cleanup:                                 ; preds = %for.cond
  br label %cleanup19, !dbg !122

for.body:                                         ; preds = %for.cond
  br label %for.cond12, !dbg !123

for.cond12:                                       ; preds = %for.body15, %for.body
  %running.0 = phi double [ 0.000000e+00, %for.body ], [ %add, %for.body15 ], !dbg !124
  %j.0 = phi i32 [ %i.0, %for.body ], [ %dec, %for.body15 ], !dbg !125
  %cmp13 = icmp sgt i32 %j.0, 0, !dbg !126
  br i1 %cmp13, label %for.body15, label %for.cond.cleanup14, !dbg !127

for.cond.cleanup14:                               ; preds = %for.cond12
  %cmp17 = fcmp contract olt double %call, %running.0, !dbg !128
  br i1 %cmp17, label %if.then, label %if.end, !dbg !129

for.body15:                                       ; preds = %for.cond12
  %idxprom = sext i32 %j.0 to i64, !dbg !130
  %arrayidx16 = getelementptr inbounds [12 x double], ptr %dist.ascast, i64 0, i64 %idxprom, !dbg !130
  %0 = load double, ptr %arrayidx16, align 8, !dbg !130, !tbaa !46
  %add = fadd contract double %running.0, %0, !dbg !131
  %dec = add nsw i32 %j.0, -1, !dbg !132
  br label %for.cond12, !dbg !127, !llvm.loop !133

if.then:                                          ; preds = %for.cond.cleanup14
  br label %cleanup, !dbg !135

if.end:                                           ; preds = %for.cond.cleanup14
  br label %cleanup, !dbg !136

cleanup:                                          ; preds = %if.end, %if.then
  %retval.1 = phi i32 [ %i.0, %if.then ], [ %retval.0, %if.end ]
  %cleanup.dest.slot.0 = phi i32 [ 1, %if.then ], [ 0, %if.end ]
  %cond24 = icmp eq i32 %cleanup.dest.slot.0, 0
  br i1 %cond24, label %for.inc18, label %cleanup19

for.inc18:                                        ; preds = %cleanup
  %inc = add nsw i32 %i.0, 1, !dbg !137
  br label %for.cond, !dbg !122, !llvm.loop !138

cleanup19:                                        ; preds = %cleanup, %for.cond.cleanup
  %retval.2 = phi i32 [ %retval.1, %cleanup ], [ %retval.0, %for.cond.cleanup ]
  %cleanup.dest.slot.1 = phi i32 [ %cleanup.dest.slot.0, %cleanup ], [ 2, %for.cond.cleanup ]
  %cond = icmp eq i32 %cleanup.dest.slot.1, 2
  br i1 %cond, label %for.end21, label %cleanup22

for.end21:                                        ; preds = %cleanup19
  br label %cleanup22, !dbg !139

cleanup22:                                        ; preds = %for.end21, %cleanup19
  %retval.3 = phi i32 [ 0, %for.end21 ], [ %retval.2, %cleanup19 ], !dbg !124
  call void @llvm.lifetime.end.p5(i64 96, ptr addrspace(5) %dist) #9, !dbg !140
  ret i32 %retval.3, !dbg !140
}
