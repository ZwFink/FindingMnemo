define protected amdgpu_kernel void @_Z25xs_lookup_kernel_baseline6Inputs14SimulationData(ptr addrspace(4) noundef byref(%struct.Inputs) align 8 %0, ptr addrspace(4) noundef byref(%struct.SimulationData) align 8 %1) local_unnamed_addr #4 !dbg !8 !proteus.jit !11 {
entry:
  %coerce.sroa.4 = alloca [12 x i8], align 4, addrspace(5)
  %coerce.sroa.6 = alloca { i32, i32, i32, i32 }, align 8, addrspace(5)
  %coerce1.sroa.7 = alloca [28 x i8], align 8, addrspace(5)
  %coerce1.sroa.9 = alloca { i32, ptr, i32, ptr, i32 }, align 8, addrspace(5)
  %seed = alloca i64, align 8, addrspace(5)
  %macro_xs_vector = alloca [5 x double], align 16, addrspace(5)
  %seed.ascast = addrspacecast ptr addrspace(5) %seed to ptr
  %macro_xs_vector.ascast = addrspacecast ptr addrspace(5) %macro_xs_vector to ptr
  %coerce.sroa.1.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 8
  %coerce.sroa.1.0.copyload = load i64, ptr addrspace(4) %coerce.sroa.1.0..sroa_idx, align 8
  %coerce.sroa.2.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 16
  %coerce.sroa.2.0.copyload = load i64, ptr addrspace(4) %coerce.sroa.2.0..sroa_idx, align 8
  %coerce.sroa.3.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 24
  %coerce.sroa.3.0.copyload = load i32, ptr addrspace(4) %coerce.sroa.3.0..sroa_idx, align 8
  %coerce.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 28
  %coerce.sroa.4.0.sroa_cast = addrspacecast ptr addrspace(5) %coerce.sroa.4 to ptr
  call void @llvm.memcpy.p0.p4.i64(ptr align 4 %coerce.sroa.4.0.sroa_cast, ptr addrspace(4) align 4 %coerce.sroa.4.0..sroa_idx, i64 12, i1 false)
  %coerce.sroa.425.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 40
  %coerce.sroa.425.0.copyload = load i32, ptr addrspace(4) %coerce.sroa.425.0..sroa_idx, align 8
  %coerce.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 44
  %coerce.sroa.5.0.copyload = load i32, ptr addrspace(4) %coerce.sroa.5.0..sroa_idx, align 4
  %coerce.sroa.6.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %0, i64 48
  %coerce.sroa.6.0.sroa_cast = addrspacecast ptr addrspace(5) %coerce.sroa.6 to ptr
  call void @llvm.memcpy.p0.p4.i64(ptr align 8 %coerce.sroa.6.0.sroa_cast, ptr addrspace(4) align 8 %coerce.sroa.6.0..sroa_idx, i64 16, i1 false)
  %coerce1.sroa.0.0.copyload = load ptr, ptr addrspace(4) %1, align 8
  %coerce1.sroa.2.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 8
  %coerce1.sroa.2.0.copyload = load ptr, ptr addrspace(4) %coerce1.sroa.2.0..sroa_idx, align 8
  %coerce1.sroa.3.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 16
  %coerce1.sroa.3.0.copyload = load ptr, ptr addrspace(4) %coerce1.sroa.3.0..sroa_idx, align 8
  %coerce1.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 24
  %coerce1.sroa.4.0.copyload = load ptr, ptr addrspace(4) %coerce1.sroa.4.0..sroa_idx, align 8
  %coerce1.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 32
  %coerce1.sroa.5.0.copyload = load ptr, ptr addrspace(4) %coerce1.sroa.5.0..sroa_idx, align 8
  %coerce1.sroa.6.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 40
  %coerce1.sroa.6.0.copyload = load ptr, ptr addrspace(4) %coerce1.sroa.6.0..sroa_idx, align 8
  %coerce1.sroa.7.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 48
  %coerce1.sroa.7.0.sroa_cast = addrspacecast ptr addrspace(5) %coerce1.sroa.7 to ptr
  call void @llvm.memcpy.p0.p4.i64(ptr align 8 %coerce1.sroa.7.0.sroa_cast, ptr addrspace(4) align 8 %coerce1.sroa.7.0..sroa_idx, i64 28, i1 false)
  %coerce1.sroa.724.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 76
  %coerce1.sroa.724.0.copyload = load i32, ptr addrspace(4) %coerce1.sroa.724.0..sroa_idx, align 4
  %coerce1.sroa.8.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 80
  %coerce1.sroa.8.0.copyload = load ptr, ptr addrspace(4) %coerce1.sroa.8.0..sroa_idx, align 8
  %coerce1.sroa.9.0..sroa_idx = getelementptr inbounds i8, ptr addrspace(4) %1, i64 88
  %coerce1.sroa.9.0.sroa_cast = addrspacecast ptr addrspace(5) %coerce1.sroa.9 to ptr
  call void @llvm.memcpy.p0.p4.i64(ptr align 8 %coerce1.sroa.9.0.sroa_cast, ptr addrspace(4) align 8 %coerce1.sroa.9.0..sroa_idx, i64 40, i1 false)
  %call = call fastcc noundef i32 @_ZN24__hip_builtin_blockIdx_t7__get_xEv() #8, !dbg !12
  %call2 = call fastcc noundef i32 @_ZN24__hip_builtin_blockDim_t7__get_xEv() #8, !dbg !13
  %mul = mul i32 %call, %call2, !dbg !14
  %call3 = call fastcc noundef i32 @_ZN25__hip_builtin_threadIdx_t7__get_xEv() #8, !dbg !15
  %add = add i32 %mul, %call3, !dbg !16
  %cmp = icmp sge i32 %add, %coerce.sroa.3.0.copyload, !dbg !17
  br i1 %cmp, label %if.then, label %if.end, !dbg !18

if.then:                                          ; preds = %entry
  br label %cleanup, !dbg !19

if.end:                                           ; preds = %entry
  call void @llvm.lifetime.start.p5(i64 8, ptr addrspace(5) %seed) #9, !dbg !20
  store i64 1070, ptr %seed.ascast, align 8, !dbg !21, !tbaa !22
  %mul4 = mul nsw i32 2, %add, !dbg !26
  %conv = sext i32 %mul4 to i64, !dbg !27
  %call5 = call fastcc noundef i64 @_Z16fast_forward_LCGmm(i64 noundef 1070, i64 noundef %conv) #8, !dbg !28
  store i64 %call5, ptr %seed.ascast, align 8, !dbg !29, !tbaa !22
  %call6 = call contract fastcc noundef double @_Z17LCG_random_doublePm(ptr noundef %seed.ascast) #8, !dbg !30
  %call7 = call fastcc noundef i32 @_Z8pick_matPm(ptr noundef %seed.ascast) #8, !dbg !31
  call void @llvm.lifetime.start.p5(i64 40, ptr addrspace(5) %macro_xs_vector) #9, !dbg !32
  call void @llvm.memset.p0.i64(ptr align 16 %macro_xs_vector.ascast, i8 0, i64 40, i1 false), !dbg !33
  call fastcc void @_Z18calculate_macro_xsdillPiPdS0_S_P16NuclideGridPointS_S0_iii(double noundef %call6, i32 noundef %call7, i64 noundef %coerce.sroa.1.0.copyload, i64 noundef %coerce.sroa.2.0.copyload, ptr noundef %coerce1.sroa.0.0.copyload, ptr noundef %coerce1.sroa.2.0.copyload, ptr noundef %coerce1.sroa.4.0.copyload, ptr noundef %coerce1.sroa.5.0.copyload, ptr noundef %coerce1.sroa.6.0.copyload, ptr noundef %coerce1.sroa.3.0.copyload, ptr noundef %macro_xs_vector.ascast, i32 noundef %coerce.sroa.425.0.copyload, i32 noundef %coerce.sroa.5.0.copyload, i32 noundef %coerce1.sroa.724.0.copyload) #8, !dbg !34
  br label %for.cond, !dbg !35

for.cond:                                         ; preds = %for.inc, %if.end
  %max.0 = phi double [ -1.000000e+00, %if.end ], [ %max.1, %for.inc ], !dbg !36
  %max_idx.0 = phi i32 [ 0, %if.end ], [ %max_idx.1, %for.inc ], !dbg !36
  %j.0 = phi i32 [ 0, %if.end ], [ %inc, %for.inc ], !dbg !37
  %cmp8 = icmp slt i32 %j.0, 5, !dbg !38
  br i1 %cmp8, label %for.body, label %for.cond.cleanup, !dbg !39

for.cond.cleanup:                                 ; preds = %for.cond
  %add14 = add nsw i32 %max_idx.0, 1, !dbg !40
  %conv15 = sext i32 %add14 to i64, !dbg !41
  %idxprom16 = sext i32 %add to i64, !dbg !42
  %arrayidx17 = getelementptr inbounds i64, ptr %coerce1.sroa.8.0.copyload, i64 %idxprom16, !dbg !42
  store i64 %conv15, ptr %arrayidx17, align 8, !dbg !43, !tbaa !22
  call void @llvm.lifetime.end.p5(i64 40, ptr addrspace(5) %macro_xs_vector) #9, !dbg !44
  call void @llvm.lifetime.end.p5(i64 8, ptr addrspace(5) %seed) #9, !dbg !44
  br label %cleanup, !dbg !44

for.body:                                         ; preds = %for.cond
  %idxprom = sext i32 %j.0 to i64, !dbg !45
  %arrayidx = getelementptr inbounds [5 x double], ptr %macro_xs_vector.ascast, i64 0, i64 %idxprom, !dbg !45
  %2 = load double, ptr %arrayidx, align 8, !dbg !45, !tbaa !46
  %cmp9 = fcmp contract ogt double %2, %max.0, !dbg !48
  br i1 %cmp9, label %if.then10, label %for.inc, !dbg !45

if.then10:                                        ; preds = %for.body
  br label %for.inc, !dbg !49

for.inc:                                          ; preds = %if.then10, %for.body
  %max.1 = phi double [ %2, %if.then10 ], [ %max.0, %for.body ], !dbg !36
  %max_idx.1 = phi i32 [ %j.0, %if.then10 ], [ %max_idx.0, %for.body ], !dbg !36
  %inc = add nsw i32 %j.0, 1, !dbg !50
  br label %for.cond, !dbg !39, !llvm.loop !51

cleanup:                                          ; preds = %for.cond.cleanup, %if.then
  ret void, !dbg !44
}
