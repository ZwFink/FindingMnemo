; ModuleID = '/p/vast1/fink12/claude-scratch/findingmnemo/script-check3/runs/xsbench-small-unionized/record-db/RecordedIR_14062985557092847525.bc'
source_filename = "/p/vast1/fink12/claude-scratch/findingmnemo/script-check3/XSBench/hip/Simulation.cpp"
target datalayout = "e-p:64:64-p1:64:64-p2:32:32-p3:32:32-p4:64:64-p5:32:32-p6:32:32-p7:160:256:256:32-p8:128:128-p9:192:256:256:32-i64:64-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024-v2048:2048-n32:64-S32-A5-G1-ni:7:8:9"
target triple = "amdgcn-amd-amdhsa"

%struct.Inputs = type { i32, i64, i64, i32, ptr, i32, i32, i32, i32, i32, i32 }
%struct.SimulationData = type { ptr, ptr, ptr, ptr, ptr, ptr, i32, i32, i32, i32, i64, i32, i32, ptr, i32, ptr, i32, ptr, i32 }
%struct.NuclideGridPoint = type { double, double, double, double, double, double }

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p5(i64 immarg, ptr addrspace(5) nocapture) #0

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p5(i64 immarg, ptr addrspace(5) nocapture) #0

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef i32 @llvm.amdgcn.workitem.id.y() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef i32 @llvm.amdgcn.workgroup.id.y() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef i32 @llvm.amdgcn.workgroup.id.z() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef i32 @llvm.amdgcn.workitem.id.z() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef i32 @llvm.amdgcn.workgroup.id.x() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef i32 @llvm.amdgcn.workitem.id.x() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare noundef align 4 ptr addrspace(4) @llvm.amdgcn.implicitarg.ptr() #1

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #2

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p4.i64(ptr noalias nocapture writeonly, ptr addrspace(4) noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: convergent mustprogress norecurse nounwind
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

; Function Attrs: alwaysinline convergent mustprogress nounwind
define internal fastcc noundef i32 @_ZN24__hip_builtin_blockIdx_t7__get_xEv() unnamed_addr #5 align 2 !dbg !54 {
entry:
  %call = call fastcc noundef i32 @_ZL21__hip_get_block_idx_xv() #8, !dbg !56
  ret i32 %call, !dbg !56
}

; Function Attrs: alwaysinline convergent mustprogress nounwind
define internal fastcc noundef i32 @_ZN24__hip_builtin_blockDim_t7__get_xEv() unnamed_addr #5 align 2 !dbg !57 {
entry:
  %call = call fastcc noundef i32 @_ZL21__hip_get_block_dim_xv() #8, !dbg !58
  ret i32 %call, !dbg !58
}

; Function Attrs: alwaysinline convergent mustprogress nounwind
define internal fastcc noundef i32 @_ZN25__hip_builtin_threadIdx_t7__get_xEv() unnamed_addr #5 align 2 !dbg !59 {
entry:
  %call = call fastcc noundef i32 @_ZL22__hip_get_thread_idx_xv() #8, !dbg !60
  ret i32 %call, !dbg !60
}

; Function Attrs: convergent mustprogress nounwind
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

; Function Attrs: convergent mustprogress nounwind
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

; Function Attrs: convergent mustprogress nounwind
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

; Function Attrs: convergent mustprogress nounwind
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

; Function Attrs: convergent mustprogress nounwind
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

; Function Attrs: convergent mustprogress nounwind
define internal fastcc void @_Z18calculate_micro_xsdillPdPiP16NuclideGridPointlS_ii(double noundef %p_energy, i32 noundef %nuc, i64 noundef %n_isotopes, i64 noundef %n_gridpoints, ptr noalias noundef %egrid, ptr noalias noundef %index_data, ptr noalias noundef %nuclide_grids, i64 noundef %idx, ptr noalias noundef %xs_vector, i32 noundef %grid_type, i32 noundef %hash_bins) unnamed_addr #6 !dbg !208 {
entry:
  %cmp = icmp eq i32 %grid_type, 1, !dbg !209
  br i1 %cmp, label %if.then, label %if.else12, !dbg !210

if.then:                                          ; preds = %entry
  %conv = sext i32 %nuc to i64, !dbg !211
  %mul = mul nsw i64 %conv, %n_gridpoints, !dbg !212
  %arrayidx = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %mul, !dbg !213
  %sub = sub nsw i64 %n_gridpoints, 1, !dbg !214
  %call = call fastcc noundef i64 @_Z19grid_search_nuclideldP16NuclideGridPointll(i64 noundef %n_gridpoints, double noundef %p_energy, ptr noundef %arrayidx, i64 noundef 0, i64 noundef %sub) #8, !dbg !215
  %cmp2 = icmp eq i64 %call, %sub, !dbg !216
  br i1 %cmp2, label %if.then3, label %if.else, !dbg !217

if.then3:                                         ; preds = %if.then
  %add = add nsw i64 %mul, %call, !dbg !218
  %sub6 = sub nsw i64 %add, 1, !dbg !219
  %arrayidx7 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %sub6, !dbg !220
  br label %if.end109, !dbg !221

if.else:                                          ; preds = %if.then
  %add10 = add nsw i64 %mul, %call, !dbg !222
  %arrayidx11 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %add10, !dbg !223
  br label %if.end109

if.else12:                                        ; preds = %entry
  %cmp13 = icmp eq i32 %grid_type, 0, !dbg !224
  br i1 %cmp13, label %if.then14, label %if.else44, !dbg !225

if.then14:                                        ; preds = %if.else12
  %mul15 = mul nsw i64 %idx, %n_isotopes, !dbg !226
  %conv16 = sext i32 %nuc to i64, !dbg !227
  %add17 = add nsw i64 %mul15, %conv16, !dbg !228
  %arrayidx18 = getelementptr inbounds i32, ptr %index_data, i64 %add17, !dbg !229
  %0 = load i32, ptr %arrayidx18, align 4, !dbg !229, !tbaa !167
  %conv19 = sext i32 %0 to i64, !dbg !229
  %sub20 = sub nsw i64 %n_gridpoints, 1, !dbg !230
  %cmp21 = icmp eq i64 %conv19, %sub20, !dbg !231
  br i1 %cmp21, label %if.then22, label %if.else33, !dbg !229

if.then22:                                        ; preds = %if.then14
  %mul24 = mul nsw i64 %conv16, %n_gridpoints, !dbg !232
  %add30 = add nsw i64 %mul24, %conv19, !dbg !233
  %sub31 = sub nsw i64 %add30, 1, !dbg !234
  %arrayidx32 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %sub31, !dbg !235
  br label %if.end109, !dbg !236

if.else33:                                        ; preds = %if.then14
  %mul35 = mul nsw i64 %conv16, %n_gridpoints, !dbg !237
  %add41 = add nsw i64 %mul35, %conv19, !dbg !238
  %arrayidx42 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %add41, !dbg !239
  br label %if.end109

if.else44:                                        ; preds = %if.else12
  %mul45 = mul nsw i64 %idx, %n_isotopes, !dbg !240
  %conv46 = sext i32 %nuc to i64, !dbg !241
  %add47 = add nsw i64 %mul45, %conv46, !dbg !242
  %arrayidx48 = getelementptr inbounds i32, ptr %index_data, i64 %add47, !dbg !243
  %1 = load i32, ptr %arrayidx48, align 4, !dbg !243, !tbaa !167
  %sub49 = sub nsw i32 %hash_bins, 1, !dbg !244
  %conv50 = sext i32 %sub49 to i64, !dbg !245
  %cmp51 = icmp eq i64 %idx, %conv50, !dbg !246
  br i1 %cmp51, label %if.then52, label %if.else55, !dbg !247

if.then52:                                        ; preds = %if.else44
  %sub53 = sub nsw i64 %n_gridpoints, 1, !dbg !248
  %conv54 = trunc i64 %sub53 to i32, !dbg !249
  br label %if.end62, !dbg !250

if.else55:                                        ; preds = %if.else44
  %add56 = add nsw i64 %idx, 1, !dbg !251
  %mul57 = mul nsw i64 %add56, %n_isotopes, !dbg !252
  %add59 = add nsw i64 %mul57, %conv46, !dbg !253
  %arrayidx60 = getelementptr inbounds i32, ptr %index_data, i64 %add59, !dbg !254
  %2 = load i32, ptr %arrayidx60, align 4, !dbg !254, !tbaa !167
  %add61 = add nsw i32 %2, 1, !dbg !255
  br label %if.end62

if.end62:                                         ; preds = %if.else55, %if.then52
  %u_high.0 = phi i32 [ %conv54, %if.then52 ], [ %add61, %if.else55 ], !dbg !256
  %mul64 = mul nsw i64 %conv46, %n_gridpoints, !dbg !257
  %conv65 = sext i32 %1 to i64, !dbg !258
  %add66 = add nsw i64 %mul64, %conv65, !dbg !259
  %arrayidx67 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %add66, !dbg !260
  %3 = load double, ptr %arrayidx67, align 8, !dbg !261, !tbaa !262
  %conv70 = sext i32 %u_high.0 to i64, !dbg !264
  %add71 = add nsw i64 %mul64, %conv70, !dbg !265
  %arrayidx72 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %add71, !dbg !266
  %4 = load double, ptr %arrayidx72, align 8, !dbg !267, !tbaa !262
  %cmp74 = fcmp contract ole double %p_energy, %3, !dbg !268
  br i1 %cmp74, label %if.then75, label %if.else76, !dbg !269

if.then75:                                        ; preds = %if.end62
  br label %if.end90, !dbg !270

if.else76:                                        ; preds = %if.end62
  %cmp77 = fcmp contract oge double %p_energy, %4, !dbg !271
  br i1 %cmp77, label %if.then78, label %if.else81, !dbg !272

if.then78:                                        ; preds = %if.else76
  %sub79 = sub nsw i64 %n_gridpoints, 1, !dbg !273
  %conv80 = trunc i64 %sub79 to i32, !dbg !274
  br label %if.end90, !dbg !275

if.else81:                                        ; preds = %if.else76
  %arrayidx84 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %mul64, !dbg !276
  %call87 = call fastcc noundef i64 @_Z19grid_search_nuclideldP16NuclideGridPointll(i64 noundef %n_gridpoints, double noundef %p_energy, ptr noundef %arrayidx84, i64 noundef %conv65, i64 noundef %conv70) #8, !dbg !277
  %conv88 = trunc i64 %call87 to i32, !dbg !277
  br label %if.end90

if.end90:                                         ; preds = %if.else81, %if.then78, %if.then75
  %lower.0 = phi i32 [ 0, %if.then75 ], [ %conv80, %if.then78 ], [ %conv88, %if.else81 ], !dbg !256
  %conv91 = sext i32 %lower.0 to i64, !dbg !278
  %sub92 = sub nsw i64 %n_gridpoints, 1, !dbg !279
  %cmp93 = icmp eq i64 %conv91, %sub92, !dbg !280
  br i1 %cmp93, label %if.then94, label %if.else101, !dbg !278

if.then94:                                        ; preds = %if.end90
  %add98 = add nsw i64 %mul64, %conv91, !dbg !281
  %sub99 = sub nsw i64 %add98, 1, !dbg !282
  %arrayidx100 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %sub99, !dbg !283
  br label %if.end107, !dbg !284

if.else101:                                       ; preds = %if.end90
  %add105 = add nsw i64 %mul64, %conv91, !dbg !285
  %arrayidx106 = getelementptr inbounds %struct.NuclideGridPoint, ptr %nuclide_grids, i64 %add105, !dbg !286
  br label %if.end107

if.end107:                                        ; preds = %if.else101, %if.then94
  %low.0 = phi ptr [ %arrayidx100, %if.then94 ], [ %arrayidx106, %if.else101 ], !dbg !256
  br label %if.end109

if.end109:                                        ; preds = %if.end107, %if.else33, %if.then22, %if.else, %if.then3
  %low.1 = phi ptr [ %arrayidx7, %if.then3 ], [ %arrayidx11, %if.else ], [ %arrayidx32, %if.then22 ], [ %arrayidx42, %if.else33 ], [ %low.0, %if.end107 ], !dbg !256
  %add.ptr = getelementptr inbounds %struct.NuclideGridPoint, ptr %low.1, i64 1, !dbg !287
  %5 = load double, ptr %add.ptr, align 8, !dbg !288, !tbaa !262
  %sub111 = fsub contract double %5, %p_energy, !dbg !289
  %6 = load double, ptr %low.1, align 8, !dbg !290, !tbaa !262
  %sub114 = fsub contract double %5, %6, !dbg !291
  %div = fdiv contract double %sub111, %sub114, !dbg !292
  %total_xs = getelementptr inbounds %struct.NuclideGridPoint, ptr %add.ptr, i32 0, i32 1, !dbg !293
  %7 = load double, ptr %total_xs, align 8, !dbg !293, !tbaa !294
  %total_xs116 = getelementptr inbounds %struct.NuclideGridPoint, ptr %low.1, i32 0, i32 1, !dbg !295
  %8 = load double, ptr %total_xs116, align 8, !dbg !295, !tbaa !294
  %sub117 = fsub contract double %7, %8, !dbg !296
  %mul118 = fmul contract double %div, %sub117, !dbg !297
  %sub119 = fsub contract double %7, %mul118, !dbg !298
  store double %sub119, ptr %xs_vector, align 8, !dbg !299, !tbaa !46
  %elastic_xs = getelementptr inbounds %struct.NuclideGridPoint, ptr %add.ptr, i32 0, i32 2, !dbg !300
  %9 = load double, ptr %elastic_xs, align 8, !dbg !300, !tbaa !301
  %elastic_xs122 = getelementptr inbounds %struct.NuclideGridPoint, ptr %low.1, i32 0, i32 2, !dbg !302
  %10 = load double, ptr %elastic_xs122, align 8, !dbg !302, !tbaa !301
  %sub123 = fsub contract double %9, %10, !dbg !303
  %mul124 = fmul contract double %div, %sub123, !dbg !304
  %sub125 = fsub contract double %9, %mul124, !dbg !305
  %arrayidx126 = getelementptr inbounds double, ptr %xs_vector, i64 1, !dbg !306
  store double %sub125, ptr %arrayidx126, align 8, !dbg !307, !tbaa !46
  %absorbtion_xs = getelementptr inbounds %struct.NuclideGridPoint, ptr %add.ptr, i32 0, i32 3, !dbg !308
  %11 = load double, ptr %absorbtion_xs, align 8, !dbg !308, !tbaa !309
  %absorbtion_xs128 = getelementptr inbounds %struct.NuclideGridPoint, ptr %low.1, i32 0, i32 3, !dbg !310
  %12 = load double, ptr %absorbtion_xs128, align 8, !dbg !310, !tbaa !309
  %sub129 = fsub contract double %11, %12, !dbg !311
  %mul130 = fmul contract double %div, %sub129, !dbg !312
  %sub131 = fsub contract double %11, %mul130, !dbg !313
  %arrayidx132 = getelementptr inbounds double, ptr %xs_vector, i64 2, !dbg !314
  store double %sub131, ptr %arrayidx132, align 8, !dbg !315, !tbaa !46
  %fission_xs = getelementptr inbounds %struct.NuclideGridPoint, ptr %add.ptr, i32 0, i32 4, !dbg !316
  %13 = load double, ptr %fission_xs, align 8, !dbg !316, !tbaa !317
  %fission_xs134 = getelementptr inbounds %struct.NuclideGridPoint, ptr %low.1, i32 0, i32 4, !dbg !318
  %14 = load double, ptr %fission_xs134, align 8, !dbg !318, !tbaa !317
  %sub135 = fsub contract double %13, %14, !dbg !319
  %mul136 = fmul contract double %div, %sub135, !dbg !320
  %sub137 = fsub contract double %13, %mul136, !dbg !321
  %arrayidx138 = getelementptr inbounds double, ptr %xs_vector, i64 3, !dbg !322
  store double %sub137, ptr %arrayidx138, align 8, !dbg !323, !tbaa !46
  %nu_fission_xs = getelementptr inbounds %struct.NuclideGridPoint, ptr %add.ptr, i32 0, i32 5, !dbg !324
  %15 = load double, ptr %nu_fission_xs, align 8, !dbg !324, !tbaa !325
  %nu_fission_xs140 = getelementptr inbounds %struct.NuclideGridPoint, ptr %low.1, i32 0, i32 5, !dbg !326
  %16 = load double, ptr %nu_fission_xs140, align 8, !dbg !326, !tbaa !325
  %sub141 = fsub contract double %15, %16, !dbg !327
  %mul142 = fmul contract double %div, %sub141, !dbg !328
  %sub143 = fsub contract double %15, %mul142, !dbg !329
  %arrayidx144 = getelementptr inbounds double, ptr %xs_vector, i64 4, !dbg !330
  store double %sub143, ptr %arrayidx144, align 8, !dbg !331, !tbaa !46
  ret void, !dbg !332
}

; Function Attrs: convergent mustprogress nounwind
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

; Function Attrs: alwaysinline convergent mustprogress nounwind
define internal fastcc noundef i32 @_ZL22__hip_get_thread_idx_xv() unnamed_addr #5 !dbg !349 {
entry:
  %call = call fastcc i64 @__ockl_get_local_id(i32 noundef 0) #10, !dbg !350
  %conv = trunc i64 %call to i32, !dbg !350
  ret i32 %conv, !dbg !351
}

; Function Attrs: convergent mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define internal fastcc range(i64 0, 1024) i64 @__ockl_get_local_id(i32 noundef %0) unnamed_addr #7 {
  switch i32 %0, label %8 [
    i32 0, label %2
    i32 1, label %4
    i32 2, label %6
  ]

2:                                                ; preds = %1
  %3 = tail call noundef range(i32 0, 1024) i32 @llvm.amdgcn.workitem.id.x()
  br label %8

4:                                                ; preds = %1
  %5 = tail call noundef range(i32 0, 1024) i32 @llvm.amdgcn.workitem.id.y()
  br label %8

6:                                                ; preds = %1
  %7 = tail call noundef range(i32 0, 1024) i32 @llvm.amdgcn.workitem.id.z()
  br label %8

8:                                                ; preds = %6, %4, %2, %1
  %9 = phi i32 [ %7, %6 ], [ %5, %4 ], [ %3, %2 ], [ 0, %1 ]
  %10 = zext nneg i32 %9 to i64
  ret i64 %10
}

; Function Attrs: alwaysinline convergent mustprogress nounwind
define internal fastcc noundef i32 @_ZL21__hip_get_block_dim_xv() unnamed_addr #5 !dbg !352 {
entry:
  %call = call fastcc i64 @__ockl_get_local_size(i32 noundef 0) #10, !dbg !353
  %conv = trunc i64 %call to i32, !dbg !353
  ret i32 %conv, !dbg !354
}

; Function Attrs: convergent mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define internal fastcc range(i64 0, 4294967296) i64 @__ockl_get_local_size(i32 noundef %0) unnamed_addr #7 {
  switch i32 %0, label %34 [
    i32 0, label %2
    i32 1, label %12
    i32 2, label %23
  ]

2:                                                ; preds = %1
  br label %3

3:                                                ; preds = %2
  %4 = tail call i32 @llvm.amdgcn.workgroup.id.x()
  %5 = tail call ptr addrspace(4) @llvm.amdgcn.implicitarg.ptr()
  %6 = load i32, ptr addrspace(4) %5, align 4, !tbaa !355
  %7 = icmp ult i32 %4, %6
  %8 = select i1 %7, i64 12, i64 18
  %9 = getelementptr inbounds i8, ptr addrspace(4) %5, i64 %8
  %10 = load i16, ptr addrspace(4) %9, align 2, !tbaa !359
  %11 = zext i16 %10 to i64
  br label %34

12:                                               ; preds = %1
  br label %13

13:                                               ; preds = %12
  %14 = tail call i32 @llvm.amdgcn.workgroup.id.y()
  %15 = tail call ptr addrspace(4) @llvm.amdgcn.implicitarg.ptr()
  %16 = getelementptr inbounds i8, ptr addrspace(4) %15, i64 4
  %17 = load i32, ptr addrspace(4) %16, align 4, !tbaa !355
  %18 = icmp ult i32 %14, %17
  %19 = select i1 %18, i64 14, i64 20
  %20 = getelementptr inbounds i8, ptr addrspace(4) %15, i64 %19
  %21 = load i16, ptr addrspace(4) %20, align 2, !tbaa !359
  %22 = zext i16 %21 to i64
  br label %34

23:                                               ; preds = %1
  br label %24

24:                                               ; preds = %23
  %25 = tail call i32 @llvm.amdgcn.workgroup.id.z()
  %26 = tail call ptr addrspace(4) @llvm.amdgcn.implicitarg.ptr()
  %27 = getelementptr inbounds i8, ptr addrspace(4) %26, i64 8
  %28 = load i32, ptr addrspace(4) %27, align 4, !tbaa !355
  %29 = icmp ult i32 %25, %28
  %30 = select i1 %29, i64 16, i64 22
  %31 = getelementptr inbounds i8, ptr addrspace(4) %26, i64 %30
  %32 = load i16, ptr addrspace(4) %31, align 2, !tbaa !359
  %33 = zext i16 %32 to i64
  br label %34

34:                                               ; preds = %24, %13, %3, %1
  %35 = phi i64 [ 1, %1 ], [ %11, %3 ], [ %22, %13 ], [ %33, %24 ]
  ret i64 %35
}

; Function Attrs: alwaysinline convergent mustprogress nounwind
define internal fastcc noundef i32 @_ZL21__hip_get_block_idx_xv() unnamed_addr #5 !dbg !361 {
entry:
  %call = call fastcc i64 @__ockl_get_group_id(i32 noundef 0) #10, !dbg !362
  %conv = trunc i64 %call to i32, !dbg !362
  ret i32 %conv, !dbg !363
}

; Function Attrs: convergent mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define internal fastcc range(i64 0, 4294967296) i64 @__ockl_get_group_id(i32 noundef %0) unnamed_addr #7 {
  switch i32 %0, label %8 [
    i32 0, label %2
    i32 1, label %4
    i32 2, label %6
  ]

2:                                                ; preds = %1
  %3 = tail call i32 @llvm.amdgcn.workgroup.id.x()
  br label %8

4:                                                ; preds = %1
  %5 = tail call i32 @llvm.amdgcn.workgroup.id.y()
  br label %8

6:                                                ; preds = %1
  %7 = tail call i32 @llvm.amdgcn.workgroup.id.z()
  br label %8

8:                                                ; preds = %6, %4, %2, %1
  %9 = phi i32 [ %7, %6 ], [ %5, %4 ], [ %3, %2 ], [ 0, %1 ]
  %10 = zext i32 %9 to i64
  ret i64 %10
}

attributes #0 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #3 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { convergent mustprogress norecurse nounwind "amdgpu-flat-work-group-size"="1,1024" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="gfx942" "target-features"="+16-bit-insts,+atomic-buffer-global-pk-add-f16-insts,+atomic-ds-pk-add-16-insts,+atomic-fadd-rtn-insts,+atomic-flat-pk-add-16-insts,+atomic-global-pk-add-bf16-inst,+ci-insts,+dl-insts,+dot1-insts,+dot10-insts,+dot2-insts,+dot3-insts,+dot4-insts,+dot5-insts,+dot6-insts,+dot7-insts,+dpp,+fp8-conversion-insts,+fp8-insts,+gfx8-insts,+gfx9-insts,+gfx90a-insts,+gfx940-insts,+mai-insts,+s-memrealtime,+s-memtime-inst,+wavefrontsize64,+xf32-insts" "uniform-work-group-size"="true" }
attributes #5 = { alwaysinline convergent mustprogress nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="gfx942" "target-features"="+16-bit-insts,+atomic-buffer-global-pk-add-f16-insts,+atomic-ds-pk-add-16-insts,+atomic-fadd-rtn-insts,+atomic-flat-pk-add-16-insts,+atomic-global-pk-add-bf16-inst,+ci-insts,+dl-insts,+dot1-insts,+dot10-insts,+dot2-insts,+dot3-insts,+dot4-insts,+dot5-insts,+dot6-insts,+dot7-insts,+dpp,+fp8-conversion-insts,+fp8-insts,+gfx8-insts,+gfx9-insts,+gfx90a-insts,+gfx940-insts,+mai-insts,+s-memrealtime,+s-memtime-inst,+wavefrontsize64,+xf32-insts" }
attributes #6 = { convergent mustprogress nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="gfx942" "target-features"="+16-bit-insts,+atomic-buffer-global-pk-add-f16-insts,+atomic-ds-pk-add-16-insts,+atomic-fadd-rtn-insts,+atomic-flat-pk-add-16-insts,+atomic-global-pk-add-bf16-inst,+ci-insts,+dl-insts,+dot1-insts,+dot10-insts,+dot2-insts,+dot3-insts,+dot4-insts,+dot5-insts,+dot6-insts,+dot7-insts,+dpp,+fp8-conversion-insts,+fp8-insts,+gfx8-insts,+gfx9-insts,+gfx90a-insts,+gfx940-insts,+mai-insts,+s-memrealtime,+s-memtime-inst,+wavefrontsize64,+xf32-insts" }
attributes #7 = { convergent mustprogress nofree norecurse nosync nounwind willreturn memory(none) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="gfx942" "target-features"="+16-bit-insts,+atomic-buffer-global-pk-add-f16-insts,+atomic-ds-pk-add-16-insts,+atomic-fadd-rtn-insts,+atomic-flat-pk-add-16-insts,+atomic-global-pk-add-bf16-inst,+ci-insts,+dl-insts,+dot1-insts,+dot10-insts,+dot2-insts,+dot3-insts,+dot4-insts,+dot5-insts,+dot6-insts,+dot7-insts,+dpp,+fp8-conversion-insts,+fp8-insts,+gfx8-insts,+gfx9-insts,+gfx90a-insts,+gfx940-insts,+gws,+mai-insts,+s-memrealtime,+s-memtime-inst,+wavefrontsize64,+xf32-insts" }
attributes #8 = { convergent nounwind }
attributes #9 = { nounwind }
attributes #10 = { convergent nounwind willreturn memory(none) }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6, !7}

!0 = distinct !DICompileUnit(language: DW_LANG_C_plus_plus_14, file: !1, producer: "AMD clang version 19.0.0git (https://github.com/RadeonOpenCompute/llvm-project roc-6.4.0 25133 c7fe45cf4b819c5991fe208aaa96edf142730f1d)", isOptimized: true, runtimeVersion: 0, emissionKind: LineTablesOnly, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "Simulation.cpp", directory: "/p/vast1/fink12/claude-scratch/findingmnemo/script-check3/XSBench/hip", checksumkind: CSK_MD5, checksum: "53acddeb86b787f1977b544879bf286f")
!2 = !{i32 1, !"amdhsa_code_object_version", i32 600}
!3 = !{i32 1, !"amdgpu_printf_kind", !"hostcall"}
!4 = !{i32 7, !"Dwarf Version", i32 5}
!5 = !{i32 4, !"Debug Info Version", i32 3}
!6 = !{i32 1, !"wchar_size", i32 4}
!7 = !{i32 8, !"PIC Level", i32 2}
!8 = distinct !DISubprogram(name: "xs_lookup_kernel_baseline", scope: !1, file: !1, line: 50, type: !9, scopeLine: 51, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!9 = !DISubroutineType(types: !10)
!10 = !{}
!11 = !{!"proteus.jit"}
!12 = !DILocation(line: 53, column: 16, scope: !8)
!13 = !DILocation(line: 53, column: 28, scope: !8)
!14 = !DILocation(line: 53, column: 27, scope: !8)
!15 = !DILocation(line: 53, column: 41, scope: !8)
!16 = !DILocation(line: 53, column: 39, scope: !8)
!17 = !DILocation(line: 55, column: 8, scope: !8)
!18 = !DILocation(line: 55, column: 6, scope: !8)
!19 = !DILocation(line: 56, column: 3, scope: !8)
!20 = !DILocation(line: 59, column: 2, scope: !8)
!21 = !DILocation(line: 59, column: 11, scope: !8)
!22 = !{!23, !23, i64 0}
!23 = !{!"long", !24, i64 0}
!24 = !{!"omnipotent char", !25, i64 0}
!25 = !{!"Simple C++ TBAA"}
!26 = !DILocation(line: 62, column: 33, scope: !8)
!27 = !DILocation(line: 62, column: 32, scope: !8)
!28 = !DILocation(line: 62, column: 9, scope: !8)
!29 = !DILocation(line: 62, column: 7, scope: !8)
!30 = !DILocation(line: 65, column: 20, scope: !8)
!31 = !DILocation(line: 66, column: 20, scope: !8)
!32 = !DILocation(line: 68, column: 2, scope: !8)
!33 = !DILocation(line: 68, column: 9, scope: !8)
!34 = !DILocation(line: 71, column: 2, scope: !8)
!35 = !DILocation(line: 96, column: 6, scope: !8)
!36 = !DILocation(line: 0, scope: !8)
!37 = !DILocation(line: 96, scope: !8)
!38 = !DILocation(line: 96, column: 19, scope: !8)
!39 = !DILocation(line: 96, column: 2, scope: !8)
!40 = !DILocation(line: 104, column: 31, scope: !8)
!41 = !DILocation(line: 104, column: 24, scope: !8)
!42 = !DILocation(line: 104, column: 2, scope: !8)
!43 = !DILocation(line: 104, column: 22, scope: !8)
!44 = !DILocation(line: 105, column: 1, scope: !8)
!45 = !DILocation(line: 98, column: 7, scope: !8)
!46 = !{!47, !47, i64 0}
!47 = !{!"double", !24, i64 0}
!48 = !DILocation(line: 98, column: 26, scope: !8)
!49 = !DILocation(line: 102, column: 3, scope: !8)
!50 = !DILocation(line: 96, column: 25, scope: !8)
!51 = distinct !{!51, !39, !52, !53}
!52 = !DILocation(line: 103, column: 2, scope: !8)
!53 = !{!"llvm.loop.mustprogress"}
!54 = distinct !DISubprogram(name: "__get_x", scope: !55, file: !55, line: 300, type: !9, scopeLine: 300, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!55 = !DIFile(filename: "/opt/rocm-6.4.0/lib/llvm/bin/../../../include/hip/amd_detail/amd_hip_runtime.h", directory: "", checksumkind: CSK_MD5, checksum: "38097f6211bac4e19f9ae3395b411f76")
!56 = !DILocation(line: 300, column: 3, scope: !54)
!57 = distinct !DISubprogram(name: "__get_x", scope: !55, file: !55, line: 309, type: !9, scopeLine: 309, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!58 = !DILocation(line: 309, column: 3, scope: !57)
!59 = distinct !DISubprogram(name: "__get_x", scope: !55, file: !55, line: 291, type: !9, scopeLine: 291, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!60 = !DILocation(line: 291, column: 3, scope: !59)
!61 = distinct !DISubprogram(name: "fast_forward_LCG", scope: !1, file: !1, line: 342, type: !9, scopeLine: 343, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!62 = !DILocation(line: 349, column: 8, scope: !61)
!63 = !DILocation(line: 354, column: 2, scope: !61)
!64 = !DILocation(line: 0, scope: !61)
!65 = !DILocation(line: 354, column: 10, scope: !61)
!66 = !DILocation(line: 356, column: 8, scope: !61)
!67 = !DILocation(line: 356, column: 6, scope: !61)
!68 = !DILocation(line: 358, column: 10, scope: !61)
!69 = !DILocation(line: 359, column: 18, scope: !61)
!70 = !DILocation(line: 359, column: 22, scope: !61)
!71 = !DILocation(line: 360, column: 3, scope: !61)
!72 = !DILocation(line: 361, column: 11, scope: !61)
!73 = !DILocation(line: 361, column: 5, scope: !61)
!74 = !DILocation(line: 362, column: 5, scope: !61)
!75 = !DILocation(line: 364, column: 5, scope: !61)
!76 = distinct !{!76, !63, !77, !53}
!77 = !DILocation(line: 365, column: 2, scope: !61)
!78 = !DILocation(line: 367, column: 16, scope: !61)
!79 = !DILocation(line: 367, column: 23, scope: !61)
!80 = !DILocation(line: 367, column: 32, scope: !61)
!81 = !DILocation(line: 367, column: 2, scope: !61)
!82 = distinct !DISubprogram(name: "LCG_random_double", scope: !1, file: !1, line: 332, type: !9, scopeLine: 333, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!83 = !DILocation(line: 338, column: 16, scope: !82)
!84 = !DILocation(line: 338, column: 13, scope: !82)
!85 = !DILocation(line: 338, column: 23, scope: !82)
!86 = !DILocation(line: 338, column: 28, scope: !82)
!87 = !DILocation(line: 338, column: 8, scope: !82)
!88 = !DILocation(line: 339, column: 18, scope: !82)
!89 = !DILocation(line: 339, column: 26, scope: !82)
!90 = !DILocation(line: 339, column: 2, scope: !82)
!91 = distinct !DISubprogram(name: "pick_mat", scope: !1, file: !1, line: 293, type: !9, scopeLine: 294, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!92 = !DILocation(line: 303, column: 2, scope: !91)
!93 = !DILocation(line: 303, column: 9, scope: !91)
!94 = !{!"auto-init"}
!95 = !DILocation(line: 304, column: 11, scope: !91)
!96 = !DILocation(line: 305, column: 2, scope: !91)
!97 = !DILocation(line: 305, column: 11, scope: !91)
!98 = !DILocation(line: 306, column: 2, scope: !91)
!99 = !DILocation(line: 306, column: 11, scope: !91)
!100 = !DILocation(line: 307, column: 2, scope: !91)
!101 = !DILocation(line: 307, column: 11, scope: !91)
!102 = !DILocation(line: 308, column: 2, scope: !91)
!103 = !DILocation(line: 308, column: 11, scope: !91)
!104 = !DILocation(line: 309, column: 2, scope: !91)
!105 = !DILocation(line: 309, column: 11, scope: !91)
!106 = !DILocation(line: 310, column: 2, scope: !91)
!107 = !DILocation(line: 310, column: 11, scope: !91)
!108 = !DILocation(line: 311, column: 2, scope: !91)
!109 = !DILocation(line: 311, column: 11, scope: !91)
!110 = !DILocation(line: 312, column: 2, scope: !91)
!111 = !DILocation(line: 312, column: 11, scope: !91)
!112 = !DILocation(line: 313, column: 2, scope: !91)
!113 = !DILocation(line: 313, column: 11, scope: !91)
!114 = !DILocation(line: 314, column: 2, scope: !91)
!115 = !DILocation(line: 314, column: 11, scope: !91)
!116 = !DILocation(line: 315, column: 2, scope: !91)
!117 = !DILocation(line: 315, column: 11, scope: !91)
!118 = !DILocation(line: 317, column: 16, scope: !91)
!119 = !DILocation(line: 320, column: 7, scope: !91)
!120 = !DILocation(line: 320, scope: !91)
!121 = !DILocation(line: 320, column: 20, scope: !91)
!122 = !DILocation(line: 320, column: 2, scope: !91)
!123 = !DILocation(line: 323, column: 8, scope: !91)
!124 = !DILocation(line: 0, scope: !91)
!125 = !DILocation(line: 323, scope: !91)
!126 = !DILocation(line: 323, column: 21, scope: !91)
!127 = !DILocation(line: 323, column: 3, scope: !91)
!128 = !DILocation(line: 325, column: 12, scope: !91)
!129 = !DILocation(line: 325, column: 7, scope: !91)
!130 = !DILocation(line: 324, column: 15, scope: !91)
!131 = !DILocation(line: 324, column: 12, scope: !91)
!132 = !DILocation(line: 323, column: 27, scope: !91)
!133 = distinct !{!133, !127, !134, !53}
!134 = !DILocation(line: 324, column: 21, scope: !91)
!135 = !DILocation(line: 326, column: 4, scope: !91)
!136 = !DILocation(line: 327, column: 2, scope: !91)
!137 = !DILocation(line: 320, column: 27, scope: !91)
!138 = distinct !{!138, !122, !136, !53}
!139 = !DILocation(line: 329, column: 2, scope: !91)
!140 = !DILocation(line: 330, column: 1, scope: !91)
!141 = distinct !DISubprogram(name: "calculate_macro_xs", scope: !1, file: !1, line: 193, type: !9, scopeLine: 199, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!142 = !DILocation(line: 205, column: 7, scope: !141)
!143 = !DILocation(line: 205, scope: !141)
!144 = !DILocation(line: 205, column: 20, scope: !141)
!145 = !DILocation(line: 205, column: 2, scope: !141)
!146 = !DILocation(line: 213, column: 16, scope: !141)
!147 = !DILocation(line: 213, column: 6, scope: !141)
!148 = !DILocation(line: 206, column: 3, scope: !141)
!149 = !DILocation(line: 206, column: 22, scope: !141)
!150 = !DILocation(line: 205, column: 26, scope: !141)
!151 = distinct !{!151, !145, !152, !53}
!152 = !DILocation(line: 206, column: 24, scope: !141)
!153 = !DILocation(line: 214, column: 33, scope: !141)
!154 = !DILocation(line: 214, column: 9, scope: !141)
!155 = !DILocation(line: 214, column: 3, scope: !141)
!156 = !DILocation(line: 215, column: 21, scope: !141)
!157 = !DILocation(line: 215, column: 11, scope: !141)
!158 = !DILocation(line: 217, column: 21, scope: !141)
!159 = !DILocation(line: 217, column: 19, scope: !141)
!160 = !DILocation(line: 218, column: 18, scope: !141)
!161 = !DILocation(line: 218, column: 9, scope: !141)
!162 = !DILocation(line: 219, column: 2, scope: !141)
!163 = !DILocation(line: 0, scope: !141)
!164 = !DILocation(line: 231, column: 7, scope: !141)
!165 = !DILocation(line: 231, scope: !141)
!166 = !DILocation(line: 231, column: 22, scope: !141)
!167 = !{!168, !168, i64 0}
!168 = !{!"int", !24, i64 0}
!169 = !DILocation(line: 231, column: 20, scope: !141)
!170 = !DILocation(line: 231, column: 2, scope: !141)
!171 = !DILocation(line: 242, column: 1, scope: !141)
!172 = !DILocation(line: 233, column: 3, scope: !141)
!173 = !DILocation(line: 233, column: 10, scope: !141)
!174 = !DILocation(line: 234, column: 19, scope: !141)
!175 = !DILocation(line: 234, column: 33, scope: !141)
!176 = !DILocation(line: 234, column: 11, scope: !141)
!177 = !DILocation(line: 235, column: 10, scope: !141)
!178 = !DILocation(line: 236, column: 3, scope: !141)
!179 = !DILocation(line: 239, column: 8, scope: !141)
!180 = !DILocation(line: 239, scope: !141)
!181 = !DILocation(line: 239, column: 21, scope: !141)
!182 = !DILocation(line: 239, column: 3, scope: !141)
!183 = !DILocation(line: 241, column: 2, scope: !141)
!184 = !DILocation(line: 231, column: 38, scope: !141)
!185 = distinct !{!185, !170, !183, !53}
!186 = !DILocation(line: 240, column: 26, scope: !141)
!187 = !DILocation(line: 240, column: 39, scope: !141)
!188 = !DILocation(line: 240, column: 4, scope: !141)
!189 = !DILocation(line: 240, column: 23, scope: !141)
!190 = !DILocation(line: 239, column: 27, scope: !141)
!191 = distinct !{!191, !182, !192, !53}
!192 = !DILocation(line: 240, column: 41, scope: !141)
!193 = distinct !DISubprogram(name: "grid_search", scope: !1, file: !1, line: 247, type: !9, scopeLine: 248, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!194 = !DILocation(line: 250, column: 21, scope: !193)
!195 = !DILocation(line: 254, column: 2, scope: !193)
!196 = !DILocation(line: 249, column: 7, scope: !193)
!197 = !DILocation(line: 0, scope: !193)
!198 = !DILocation(line: 254, column: 16, scope: !193)
!199 = !DILocation(line: 256, column: 44, scope: !193)
!200 = !DILocation(line: 256, column: 33, scope: !193)
!201 = !DILocation(line: 258, column: 7, scope: !193)
!202 = !DILocation(line: 258, column: 27, scope: !193)
!203 = !DILocation(line: 259, column: 4, scope: !193)
!204 = !DILocation(line: 263, column: 23, scope: !193)
!205 = distinct !{!205, !195, !206, !53}
!206 = !DILocation(line: 264, column: 2, scope: !193)
!207 = !DILocation(line: 266, column: 2, scope: !193)
!208 = distinct !DISubprogram(name: "calculate_micro_xs", scope: !1, file: !1, line: 108, type: !9, scopeLine: 112, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!209 = !DILocation(line: 119, column: 16, scope: !208)
!210 = !DILocation(line: 119, column: 6, scope: !208)
!211 = !DILocation(line: 122, column: 69, scope: !208)
!212 = !DILocation(line: 122, column: 72, scope: !208)
!213 = !DILocation(line: 122, column: 55, scope: !208)
!214 = !DILocation(line: 122, column: 103, scope: !208)
!215 = !DILocation(line: 122, column: 9, scope: !208)
!216 = !DILocation(line: 126, column: 11, scope: !208)
!217 = !DILocation(line: 126, column: 7, scope: !208)
!218 = !DILocation(line: 127, column: 42, scope: !208)
!219 = !DILocation(line: 127, column: 48, scope: !208)
!220 = !DILocation(line: 127, column: 11, scope: !208)
!221 = !DILocation(line: 127, column: 4, scope: !208)
!222 = !DILocation(line: 129, column: 42, scope: !208)
!223 = !DILocation(line: 129, column: 11, scope: !208)
!224 = !DILocation(line: 131, column: 21, scope: !208)
!225 = !DILocation(line: 131, column: 11, scope: !208)
!226 = !DILocation(line: 135, column: 22, scope: !208)
!227 = !DILocation(line: 135, column: 37, scope: !208)
!228 = !DILocation(line: 135, column: 35, scope: !208)
!229 = !DILocation(line: 135, column: 7, scope: !208)
!230 = !DILocation(line: 135, column: 58, scope: !208)
!231 = !DILocation(line: 135, column: 42, scope: !208)
!232 = !DILocation(line: 136, column: 28, scope: !208)
!233 = !DILocation(line: 136, column: 42, scope: !208)
!234 = !DILocation(line: 136, column: 79, scope: !208)
!235 = !DILocation(line: 136, column: 11, scope: !208)
!236 = !DILocation(line: 136, column: 4, scope: !208)
!237 = !DILocation(line: 138, column: 28, scope: !208)
!238 = !DILocation(line: 138, column: 42, scope: !208)
!239 = !DILocation(line: 138, column: 11, scope: !208)
!240 = !DILocation(line: 143, column: 30, scope: !208)
!241 = !DILocation(line: 143, column: 45, scope: !208)
!242 = !DILocation(line: 143, column: 43, scope: !208)
!243 = !DILocation(line: 143, column: 15, scope: !208)
!244 = !DILocation(line: 147, column: 24, scope: !208)
!245 = !DILocation(line: 147, column: 14, scope: !208)
!246 = !DILocation(line: 147, column: 11, scope: !208)
!247 = !DILocation(line: 147, column: 7, scope: !208)
!248 = !DILocation(line: 148, column: 26, scope: !208)
!249 = !DILocation(line: 148, column: 13, scope: !208)
!250 = !DILocation(line: 148, column: 4, scope: !208)
!251 = !DILocation(line: 150, column: 28, scope: !208)
!252 = !DILocation(line: 150, column: 31, scope: !208)
!253 = !DILocation(line: 150, column: 43, scope: !208)
!254 = !DILocation(line: 150, column: 13, scope: !208)
!255 = !DILocation(line: 150, column: 50, scope: !208)
!256 = !DILocation(line: 0, scope: !208)
!257 = !DILocation(line: 155, column: 36, scope: !208)
!258 = !DILocation(line: 155, column: 52, scope: !208)
!259 = !DILocation(line: 155, column: 50, scope: !208)
!260 = !DILocation(line: 155, column: 19, scope: !208)
!261 = !DILocation(line: 155, column: 59, scope: !208)
!262 = !{!263, !47, i64 0}
!263 = !{!"_ZTS16NuclideGridPoint", !47, i64 0, !47, i64 8, !47, i64 16, !47, i64 24, !47, i64 32, !47, i64 40}
!264 = !DILocation(line: 156, column: 52, scope: !208)
!265 = !DILocation(line: 156, column: 50, scope: !208)
!266 = !DILocation(line: 156, column: 19, scope: !208)
!267 = !DILocation(line: 156, column: 60, scope: !208)
!268 = !DILocation(line: 158, column: 16, scope: !208)
!269 = !DILocation(line: 158, column: 7, scope: !208)
!270 = !DILocation(line: 159, column: 4, scope: !208)
!271 = !DILocation(line: 160, column: 21, scope: !208)
!272 = !DILocation(line: 160, column: 12, scope: !208)
!273 = !DILocation(line: 161, column: 25, scope: !208)
!274 = !DILocation(line: 161, column: 12, scope: !208)
!275 = !DILocation(line: 161, column: 4, scope: !208)
!276 = !DILocation(line: 163, column: 58, scope: !208)
!277 = !DILocation(line: 163, column: 12, scope: !208)
!278 = !DILocation(line: 165, column: 7, scope: !208)
!279 = !DILocation(line: 165, column: 29, scope: !208)
!280 = !DILocation(line: 165, column: 13, scope: !208)
!281 = !DILocation(line: 166, column: 42, scope: !208)
!282 = !DILocation(line: 166, column: 50, scope: !208)
!283 = !DILocation(line: 166, column: 11, scope: !208)
!284 = !DILocation(line: 166, column: 4, scope: !208)
!285 = !DILocation(line: 168, column: 42, scope: !208)
!286 = !DILocation(line: 168, column: 11, scope: !208)
!287 = !DILocation(line: 171, column: 13, scope: !208)
!288 = !DILocation(line: 174, column: 13, scope: !208)
!289 = !DILocation(line: 174, column: 20, scope: !208)
!290 = !DILocation(line: 174, column: 55, scope: !208)
!291 = !DILocation(line: 174, column: 48, scope: !208)
!292 = !DILocation(line: 174, column: 32, scope: !208)
!293 = !DILocation(line: 177, column: 23, scope: !208)
!294 = !{!263, !47, i64 8}
!295 = !DILocation(line: 177, column: 61, scope: !208)
!296 = !DILocation(line: 177, column: 54, scope: !208)
!297 = !DILocation(line: 177, column: 36, scope: !208)
!298 = !DILocation(line: 177, column: 32, scope: !208)
!299 = !DILocation(line: 177, column: 15, scope: !208)
!300 = !DILocation(line: 180, column: 23, scope: !208)
!301 = !{!263, !47, i64 16}
!302 = !DILocation(line: 180, column: 65, scope: !208)
!303 = !DILocation(line: 180, column: 58, scope: !208)
!304 = !DILocation(line: 180, column: 38, scope: !208)
!305 = !DILocation(line: 180, column: 34, scope: !208)
!306 = !DILocation(line: 180, column: 2, scope: !208)
!307 = !DILocation(line: 180, column: 15, scope: !208)
!308 = !DILocation(line: 183, column: 23, scope: !208)
!309 = !{!263, !47, i64 24}
!310 = !DILocation(line: 183, column: 71, scope: !208)
!311 = !DILocation(line: 183, column: 64, scope: !208)
!312 = !DILocation(line: 183, column: 41, scope: !208)
!313 = !DILocation(line: 183, column: 37, scope: !208)
!314 = !DILocation(line: 183, column: 2, scope: !208)
!315 = !DILocation(line: 183, column: 15, scope: !208)
!316 = !DILocation(line: 186, column: 23, scope: !208)
!317 = !{!263, !47, i64 32}
!318 = !DILocation(line: 186, column: 65, scope: !208)
!319 = !DILocation(line: 186, column: 58, scope: !208)
!320 = !DILocation(line: 186, column: 38, scope: !208)
!321 = !DILocation(line: 186, column: 34, scope: !208)
!322 = !DILocation(line: 186, column: 2, scope: !208)
!323 = !DILocation(line: 186, column: 15, scope: !208)
!324 = !DILocation(line: 189, column: 23, scope: !208)
!325 = !{!263, !47, i64 40}
!326 = !DILocation(line: 189, column: 71, scope: !208)
!327 = !DILocation(line: 189, column: 64, scope: !208)
!328 = !DILocation(line: 189, column: 41, scope: !208)
!329 = !DILocation(line: 189, column: 37, scope: !208)
!330 = !DILocation(line: 189, column: 2, scope: !208)
!331 = !DILocation(line: 189, column: 15, scope: !208)
!332 = !DILocation(line: 190, column: 1, scope: !208)
!333 = distinct !DISubprogram(name: "grid_search_nuclide", scope: !1, file: !1, line: 270, type: !9, scopeLine: 271, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!334 = !DILocation(line: 275, column: 27, scope: !333)
!335 = !DILocation(line: 277, column: 2, scope: !333)
!336 = !DILocation(line: 272, column: 7, scope: !333)
!337 = !DILocation(line: 0, scope: !333)
!338 = !DILocation(line: 277, column: 16, scope: !333)
!339 = !DILocation(line: 279, column: 44, scope: !333)
!340 = !DILocation(line: 279, column: 33, scope: !333)
!341 = !DILocation(line: 281, column: 7, scope: !333)
!342 = !DILocation(line: 281, column: 27, scope: !333)
!343 = !DILocation(line: 281, column: 34, scope: !333)
!344 = !DILocation(line: 282, column: 4, scope: !333)
!345 = !DILocation(line: 286, column: 23, scope: !333)
!346 = distinct !{!346, !335, !347, !53}
!347 = !DILocation(line: 287, column: 2, scope: !333)
!348 = !DILocation(line: 289, column: 2, scope: !333)
!349 = distinct !DISubprogram(name: "__hip_get_thread_idx_x", scope: !55, file: !55, line: 265, type: !9, scopeLine: 265, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!350 = !DILocation(line: 265, column: 59, scope: !349)
!351 = !DILocation(line: 265, column: 52, scope: !349)
!352 = distinct !DISubprogram(name: "__hip_get_block_dim_x", scope: !55, file: !55, line: 275, type: !9, scopeLine: 275, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!353 = !DILocation(line: 275, column: 58, scope: !352)
!354 = !DILocation(line: 275, column: 51, scope: !352)
!355 = !{!356, !356, i64 0}
!356 = !{!"int", !357, i64 0}
!357 = !{!"omnipotent char", !358, i64 0}
!358 = !{!"Simple C/C++ TBAA"}
!359 = !{!360, !360, i64 0}
!360 = !{!"short", !357, i64 0}
!361 = distinct !DISubprogram(name: "__hip_get_block_idx_x", scope: !55, file: !55, line: 270, type: !9, scopeLine: 270, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !0)
!362 = !DILocation(line: 270, column: 58, scope: !361)
!363 = !DILocation(line: 270, column: 51, scope: !361)
