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
