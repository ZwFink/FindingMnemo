define internal fastcc void @_Z18calculate_macro_xsdillPiPdS0_S_P16NuclideGridPointS_S0_iii(double noundef %p_energy, i32 noundef %mat, i64 noundef %n_isotopes, i64 noundef %n_gridpoints, ptr noalias noundef %num_nucs, ptr noalias noundef %concs, ptr noalias noundef %egrid, ptr noalias noundef %index_data, ptr noalias noundef %nuclide_grids, ptr noalias noundef %mats, ptr noalias noundef %macro_xs_vector, i32 noundef %grid_type, i32 noundef %hash_bins, i32 noundef %max_num_nucs) unnamed_addr #6 !dbg !141 {
entry:
  %xs_vector = alloca [5 x double], align 16, addrspace(5)
  %xs_vector.ascast = addrspacecast ptr addrspace(5) %xs_vector to ptr
  br label %for.cond, !dbg !142

for.cond:                                         ; preds = %for.body, %entry
  %k.0 = phi i32 [ 0, %entry ], [ %inc, %for.body ], !dbg !143
  %cmp = icmp slt i32 %k.0, 5, !dbg !144
  br i1 %cmp, label %for.body, label %for.cond.cleanup, !dbg !145

for.cond.cleanup:                                 ; preds = %for.cond
  %cmp1 = icmp eq i32 %grid_type, 0, !dbg !146
  br i1 %cmp1, label %if.then, label %if.else, !dbg !147

for.body:                                         ; preds = %for.cond
  %idxprom = sext i32 %k.0 to i64, !dbg !148
  %arrayidx = getelementptr inbounds double, ptr %macro_xs_vector, i64 %idxprom, !dbg !148
  store double 0.000000e+00, ptr %arrayidx, align 8, !dbg !149, !tbaa !46
  %inc = add nsw i32 %k.0, 1, !dbg !150
  br label %for.cond, !dbg !145, !llvm.loop !151

if.then:                                          ; preds = %for.cond.cleanup
  %mul = mul nsw i64 %n_isotopes, %n_gridpoints, !dbg !153
  %call = call fastcc noundef i64 @_Z11grid_searchldPd(i64 noundef %mul, double noundef %p_energy, ptr noundef %egrid) #8, !dbg !154
  br label %if.end6, !dbg !155

if.else:                                          ; preds = %for.cond.cleanup
  %cmp2 = icmp eq i32 %grid_type, 2, !dbg !156
  br i1 %cmp2, label %if.then3, label %if.end6, !dbg !157

if.then3:                                         ; preds = %if.else
  %conv = sitofp i32 %hash_bins to double, !dbg !158
  %div = fdiv contract double 1.000000e+00, %conv, !dbg !159
  %div4 = fdiv contract double %p_energy, %div, !dbg !160
  %conv5 = fptosi double %div4 to i64, !dbg !161
  br label %if.end6, !dbg !162

if.end6:                                          ; preds = %if.then3, %if.else, %if.then
  %idx.0 = phi i64 [ %call, %if.then ], [ %conv5, %if.then3 ], [ -1, %if.else ], !dbg !163
  br label %for.cond7, !dbg !164

for.cond7:                                        ; preds = %for.cond.cleanup24, %if.end6
  %j.0 = phi i32 [ 0, %if.end6 ], [ %inc36, %for.cond.cleanup24 ], !dbg !165
  %idxprom8 = sext i32 %mat to i64, !dbg !166
  %arrayidx9 = getelementptr inbounds i32, ptr %num_nucs, i64 %idxprom8, !dbg !166
  %0 = load i32, ptr %arrayidx9, align 4, !dbg !166, !tbaa !167
  %cmp10 = icmp slt i32 %j.0, %0, !dbg !169
  br i1 %cmp10, label %for.body13, label %for.cond.cleanup11, !dbg !170

for.cond.cleanup11:                               ; preds = %for.cond7
  ret void, !dbg !171

for.body13:                                       ; preds = %for.cond7
  call void @llvm.lifetime.start.p5(i64 40, ptr addrspace(5) %xs_vector) #9, !dbg !172
  call void @llvm.memset.p0.i64(ptr align 16 %xs_vector.ascast, i8 0, i64 40, i1 false), !dbg !173, !annotation !94
  %mul14 = mul nsw i32 %mat, %max_num_nucs, !dbg !174
  %add = add nsw i32 %mul14, %j.0, !dbg !175
  %idxprom15 = sext i32 %add to i64, !dbg !176
  %arrayidx16 = getelementptr inbounds i32, ptr %mats, i64 %idxprom15, !dbg !176
  %1 = load i32, ptr %arrayidx16, align 4, !dbg !176, !tbaa !167
  %arrayidx20 = getelementptr inbounds double, ptr %concs, i64 %idxprom15, !dbg !177
  %2 = load double, ptr %arrayidx20, align 8, !dbg !177, !tbaa !46
  call fastcc void @_Z18calculate_micro_xsdillPdPiP16NuclideGridPointlS_ii(double noundef %p_energy, i32 noundef %1, i64 noundef %n_isotopes, i64 noundef %n_gridpoints, ptr noundef %egrid, ptr noundef %index_data, ptr noundef %nuclide_grids, i64 noundef %idx.0, ptr noundef %xs_vector.ascast, i32 noundef %grid_type, i32 noundef %hash_bins) #8, !dbg !178
  br label %for.cond22, !dbg !179

for.cond22:                                       ; preds = %for.body25, %for.body13
  %k21.0 = phi i32 [ 0, %for.body13 ], [ %inc33, %for.body25 ], !dbg !180
  %cmp23 = icmp slt i32 %k21.0, 5, !dbg !181
  br i1 %cmp23, label %for.body25, label %for.cond.cleanup24, !dbg !182

for.cond.cleanup24:                               ; preds = %for.cond22
  call void @llvm.lifetime.end.p5(i64 40, ptr addrspace(5) %xs_vector) #9, !dbg !183
  %inc36 = add nsw i32 %j.0, 1, !dbg !184
  br label %for.cond7, !dbg !170, !llvm.loop !185

for.body25:                                       ; preds = %for.cond22
  %idxprom26 = sext i32 %k21.0 to i64, !dbg !186
  %arrayidx27 = getelementptr inbounds [5 x double], ptr %xs_vector.ascast, i64 0, i64 %idxprom26, !dbg !186
  %3 = load double, ptr %arrayidx27, align 8, !dbg !186, !tbaa !46
  %mul28 = fmul contract double %3, %2, !dbg !187
  %arrayidx30 = getelementptr inbounds double, ptr %macro_xs_vector, i64 %idxprom26, !dbg !188
  %4 = load double, ptr %arrayidx30, align 8, !dbg !189, !tbaa !46
  %add31 = fadd contract double %4, %mul28, !dbg !189
  store double %add31, ptr %arrayidx30, align 8, !dbg !189, !tbaa !46
  %inc33 = add nsw i32 %k21.0, 1, !dbg !190
  br label %for.cond22, !dbg !182, !llvm.loop !191
}
