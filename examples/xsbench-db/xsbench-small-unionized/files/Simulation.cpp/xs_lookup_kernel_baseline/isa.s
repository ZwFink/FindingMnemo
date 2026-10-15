; _Z25xs_lookup_kernel_baseline6Inputs14SimulationData():
; /opt/rocm-6.4.0/lib/llvm/bin/../../../include/hip/amd_detail/amd_hip_runtime.h:275
	s_load_dword s3, s[0:1], 0xcc                              // 000000006D00: C00200C0 000000CC
	s_load_dword s4, s[0:1], 0x18                              // 000000006D08: C0020100 00000018
	s_waitcnt lgkmcnt(0)                                       // 000000006D10: BF8CC07F
	s_and_b32 s3, s3, 0xffff                                   // 000000006D14: 8603FF03 0000FFFF
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:53
	s_mul_i32 s2, s2, s3                                       // 000000006D1C: 92020302
	v_add_u32_e32 v0, s2, v0                                   // 000000006D20: 68000002
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:55
	v_cmp_gt_i32_e32 vcc, s4, v0                               // 000000006D24: 7D880004
	s_and_saveexec_b64 s[2:3], vcc                             // 000000006D28: BE82206A
	s_cbranch_execz 725                                        // 000000006D2C: BF8802D5 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xb84>
	s_load_dwordx2 s[22:23], s[0:1], 0x28                      // 000000006D30: C0060580 00000028
	s_load_dwordx8 s[4:11], s[0:1], 0x40                       // 000000006D38: C00E0100 00000040
	s_load_dwordx4 s[12:15], s[0:1], 0x60                      // 000000006D40: C00A0300 00000060
	s_load_dwordx2 s[20:21], s[0:1], 0x90                      // 000000006D48: C0060500 00000090
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:62
	v_lshlrev_b32_e32 v4, 1, v0                                // 000000006D50: 24080081
	v_ashrrev_i32_e32 v1, 31, v4                               // 000000006D54: 2202089F
	s_mov_b32 s2, 0x4a2bcaa7                                   // 000000006D58: BE8200FF 4A2BCAA7
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:349
	v_and_b32_e32 v5, 0x7fffffff, v1                           // 000000006D60: 260A02FF 7FFFFFFF
	s_mov_b32 s3, 0x45df23cb                                   // 000000006D68: BE8300FF 45DF23CB
	s_mov_b64 s[16:17], 0                                      // 000000006D70: BE900180
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:354
	v_cmp_ne_u64_e32 vcc, 0, v[4:5]                            // 000000006D74: 7DDA0880
	v_mov_b64_e32 v[2:3], s[2:3]                               // 000000006D78: 7E047002
	s_and_saveexec_b64 s[2:3], vcc                             // 000000006D7C: BE82206A
	s_cbranch_execz 74                                         // 000000006D80: BF88004A <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x1ac>
	s_mov_b64 s[18:19], 1                                      // 000000006D84: BE920181
	s_mov_b32 s27, 0x26f19d38                                  // 000000006D88: BE9B00FF 26F19D38
	s_mov_b32 s26, 0xe48e2825                                  // 000000006D90: BE9A00FF E48E2825
	v_mov_b64_e32 v[6:7], 0                                    // 000000006D98: 7E0C7080
	v_mov_b64_e32 v[2:3], 1                                    // 000000006D9C: 7E047081
	s_branch 21                                                // 000000006DA0: BF820015 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xf8>
	s_or_b64 exec, exec, s[24:25]                              // 000000006DA4: 87FE187E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:361
	s_add_u32 s24, s26, 1                                      // 000000006DA8: 8018811A
	s_addc_u32 s25, s27, 0                                     // 000000006DAC: 8219801B
	s_mul_i32 s19, s24, s19                                    // 000000006DB0: 92131318
	s_mul_hi_u32 s28, s24, s18                                 // 000000006DB4: 961C1218
	s_add_i32 s19, s28, s19                                    // 000000006DB8: 8113131C
	s_mul_i32 s25, s25, s18                                    // 000000006DBC: 92191219
	s_add_i32 s19, s19, s25                                    // 000000006DC0: 81131913
	s_mul_i32 s18, s24, s18                                    // 000000006DC4: 92121218
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:362
	s_mul_i32 s24, s26, s27                                    // 000000006DC8: 92181B1A
	s_mul_hi_u32 s25, s26, s26                                 // 000000006DCC: 96191A1A
	s_add_i32 s25, s25, s24                                    // 000000006DD0: 81191819
	s_add_i32 s27, s25, s24                                    // 000000006DD4: 811B1819
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:364
	v_lshrrev_b64 v[8:9], 1, v[4:5]                            // 000000006DD8: D2900008 00020881
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:354
	v_cmp_gt_u64_e32 vcc, 2, v[4:5]                            // 000000006DE0: 7DD80882
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:362
	s_mul_i32 s26, s26, s26                                    // 000000006DE4: 921A1A1A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:354
	s_or_b64 s[16:17], vcc, s[16:17]                           // 000000006DE8: 8790106A
	v_mov_b64_e32 v[4:5], v[8:9]                               // 000000006DEC: 7E087108
	s_andn2_b64 exec, exec, s[16:17]                           // 000000006DF0: 89FE107E
	s_cbranch_execz 23                                         // 000000006DF4: BF880017 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x154>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:356
	v_and_b32_e32 v1, 1, v4                                    // 000000006DF8: 26020881
	v_cmp_eq_u32_e32 vcc, 1, v1                                // 000000006DFC: 7D940281
	s_and_saveexec_b64 s[24:25], vcc                           // 000000006E00: BE98206A
	s_cbranch_execz 65511                                      // 000000006E04: BF88FFE7 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xa4>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:358
	v_mul_lo_u32 v1, s27, v2                                   // 000000006E08: D2850001 0002041B
	v_mul_lo_u32 v8, s26, v3                                   // 000000006E10: D2850008 0002061A
	v_mad_u64_u32 v[2:3], s[28:29], s26, v2, 0                 // 000000006E18: D1E81C02 0202041A
	v_add3_u32 v3, v3, v8, v1                                  // 000000006E20: D1FF0003 04061103
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:359
	v_mov_b64_e32 v[8:9], s[18:19]                             // 000000006E28: 7E107012
	v_mad_u64_u32 v[8:9], s[28:29], s26, v6, v[8:9]            // 000000006E2C: D1E81C08 04220C1A
	v_mul_lo_u32 v1, s26, v7                                   // 000000006E34: D2850001 00020E1A
	v_mul_lo_u32 v6, s27, v6                                   // 000000006E3C: D2850006 00020C1B
	v_add3_u32 v9, v6, v9, v1                                  // 000000006E44: D1FF0009 04061306
	v_mov_b64_e32 v[6:7], v[8:9]                               // 000000006E4C: 7E0C7108
	s_branch 65492                                             // 000000006E50: BF82FFD4 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xa4>
	s_or_b64 exec, exec, s[16:17]                              // 000000006E54: 87FE107E
	s_movk_i32 s18, 0x42e                                      // 000000006E58: B012042E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:367
	v_mad_u64_u32 v[4:5], s[16:17], v2, s18, v[6:7]            // 000000006E5C: D1E81004 04182502
	v_mov_b32_e32 v2, v5                                       // 000000006E64: 7E040305
	v_mad_u64_u32 v[2:3], s[16:17], v3, s18, v[2:3]            // 000000006E68: D1E81002 04082503
	s_mov_b32 s16, 0x26f19d38                                  // 000000006E70: BE9000FF 26F19D38
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:338
	s_nop 0                                                    // 000000006E78: BF800000
	v_mul_lo_u32 v1, v4, s16                                   // 000000006E7C: D2850001 00002104
	s_mov_b32 s16, 0xe48e2825                                  // 000000006E84: BE9000FF E48E2825
	v_mul_lo_u32 v5, v2, s16                                   // 000000006E8C: D2850005 00002102
	v_mad_u64_u32 v[2:3], s[16:17], v4, s16, 1                 // 000000006E94: D1E81002 02042104
	v_add3_u32 v1, v5, v3, v1                                  // 000000006E9C: D1FF0001 04060705
	v_and_b32_e32 v3, 0x7fffffff, v1                           // 000000006EA4: 260602FF 7FFFFFFF
	s_or_b64 exec, exec, s[2:3]                                // 000000006EAC: 87FE027E
	s_mov_b32 s2, 0xe48e2825                                   // 000000006EB0: BE8200FF E48E2825
	s_load_dwordx4 s[16:19], s[0:1], 0x8                       // 000000006EB8: C00A0400 00000008
	s_load_dword s44, s[0:1], 0x8c                             // 000000006EC0: C0020B00 0000008C
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:338
	v_mad_u64_u32 v[4:5], s[0:1], v2, s2, 1                    // 000000006EC8: D1E80004 02040502
	s_mov_b32 s0, 0x26f19d38                                   // 000000006ED0: BE8000FF 26F19D38
	s_nop 0                                                    // 000000006ED8: BF800000
	v_mul_lo_u32 v1, v2, s0                                    // 000000006EDC: D2850001 00000102
	v_mul_lo_u32 v6, v3, s2                                    // 000000006EE4: D2850006 00000503
	v_add3_u32 v1, v6, v5, v1                                  // 000000006EEC: D1FF0001 04060B06
	v_and_b32_e32 v1, 0x7fffffff, v1                           // 000000006EF4: 260202FF 7FFFFFFF
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:339
	v_cvt_f64_u32_e32 v[6:7], v1                               // 000000006EFC: 7E0C2D01
	v_ldexp_f64 v[6:7], v[6:7], 32                             // 000000006F00: D2840006 00014106
	v_cvt_f64_u32_e32 v[4:5], v4                               // 000000006F08: 7E082D04
	v_add_f64 v[4:5], v[6:7], v[4:5]                           // 000000006F0C: D2800004 00020906
	s_movk_i32 s0, 0xffc1                                      // 000000006F14: B000FFC1
	v_ldexp_f64 v[4:5], v[4:5], s0                             // 000000006F18: D2840004 00000104
	s_mov_b32 s0, 0x76c8b439                                   // 000000006F20: BE8000FF 76C8B439
	s_mov_b32 s1, 0x3faa9fbe                                   // 000000006F28: BE8100FF 3FAA9FBE
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[0:1], v[4:5]                      // 000000006F30: 7CD60800
	v_mov_b32_e32 v1, 1                                        // 000000006F34: 7E020281
	s_and_saveexec_b64 s[0:1], vcc                             // 000000006F38: BE80206A
	s_cbranch_execz 90                                         // 000000006F3C: BF88005A <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x3a8>
	s_mov_b32 s2, 0x6872b021                                   // 000000006F40: BE8200FF 6872B021
	s_mov_b32 s3, 0x3fd4ed91                                   // 000000006F48: BE8300FF 3FD4ED91
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[2:3], v[4:5]                      // 000000006F50: 7CD60802
	v_mov_b32_e32 v1, 2                                        // 000000006F54: 7E020282
	s_and_saveexec_b64 s[2:3], vcc                             // 000000006F58: BE82206A
	s_cbranch_execz 81                                         // 000000006F5C: BF880051 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x3a4>
	s_mov_b32 s24, 0x24dd2f1b                                  // 000000006F60: BE9800FF 24DD2F1B
	s_mov_b32 s25, 0x3fdd8106                                  // 000000006F68: BE9900FF 3FDD8106
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[24:25], v[4:5]                    // 000000006F70: 7CD60818
	v_mov_b32_e32 v1, 3                                        // 000000006F74: 7E020283
	s_and_saveexec_b64 s[24:25], vcc                           // 000000006F78: BE98206A
	s_cbranch_execz 72                                         // 000000006F7C: BF880048 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x3a0>
	s_mov_b32 s26, 0x7ae147af                                  // 000000006F80: BE9A00FF 7AE147AF
	s_mov_b32 s27, 0x3fe3ae14                                  // 000000006F88: BE9B00FF 3FE3AE14
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[26:27], v[4:5]                    // 000000006F90: 7CD6081A
	v_mov_b32_e32 v1, 4                                        // 000000006F94: 7E020284
	s_and_saveexec_b64 s[26:27], vcc                           // 000000006F98: BE9A206A
	s_cbranch_execz 63                                         // 000000006F9C: BF88003F <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x39c>
	s_mov_b32 s28, 0x353f7cee                                  // 000000006FA0: BE9C00FF 353F7CEE
	s_mov_b32 s29, 0x3fe5ba5e                                  // 000000006FA8: BE9D00FF 3FE5BA5E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[28:29], v[4:5]                    // 000000006FB0: 7CD6081C
	v_mov_b32_e32 v1, 5                                        // 000000006FB4: 7E020285
	s_and_saveexec_b64 s[28:29], vcc                           // 000000006FB8: BE9C206A
	s_cbranch_execz 54                                         // 000000006FBC: BF880036 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x398>
	s_mov_b32 s30, 0x3d70a3d8                                  // 000000006FC0: BE9E00FF 3D70A3D8
	s_mov_b32 s31, 0x3fe7d70a                                  // 000000006FC8: BE9F00FF 3FE7D70A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[30:31], v[4:5]                    // 000000006FD0: 7CD6081E
	v_mov_b32_e32 v1, 6                                        // 000000006FD4: 7E020286
	s_and_saveexec_b64 s[30:31], vcc                           // 000000006FD8: BE9E206A
	s_cbranch_execz 45                                         // 000000006FDC: BF88002D <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x394>
	s_mov_b32 s34, 0x9999999a                                  // 000000006FE0: BEA200FF 9999999A
	s_mov_b32 s35, 0x3fe99999                                  // 000000006FE8: BEA300FF 3FE99999
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[34:35], v[4:5]                    // 000000006FF0: 7CD60822
	v_mov_b32_e32 v1, 7                                        // 000000006FF4: 7E020287
	s_and_saveexec_b64 s[34:35], vcc                           // 000000006FF8: BEA2206A
	s_cbranch_execz 36                                         // 000000006FFC: BF880024 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x390>
	s_mov_b32 s36, 0xd0e56042                                  // 000000007000: BEA400FF D0E56042
	s_mov_b32 s37, 0x3fe9db22                                  // 000000007008: BEA500FF 3FE9DB22
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[36:37], v[4:5]                    // 000000007010: 7CD60824
	v_mov_b32_e32 v1, 8                                        // 000000007014: 7E020288
	s_and_saveexec_b64 s[36:37], vcc                           // 000000007018: BEA4206A
	s_cbranch_execz 27                                         // 00000000701C: BF88001B <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x38c>
	s_mov_b32 s38, 0x189374bd                                  // 000000007020: BEA600FF 189374BD
	s_mov_b32 s39, 0x3fea5604                                  // 000000007028: BEA700FF 3FEA5604
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[38:39], v[4:5]                    // 000000007030: 7CD60826
	v_mov_b32_e32 v1, 9                                        // 000000007034: 7E020289
	s_and_saveexec_b64 s[38:39], vcc                           // 000000007038: BEA6206A
	s_cbranch_execz 18                                         // 00000000703C: BF880012 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x388>
	s_mov_b32 s40, 0xe560418a                                  // 000000007040: BEA800FF E560418A
	s_mov_b32 s41, 0x3feb22d0                                  // 000000007048: BEA900FF 3FEB22D0
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[40:41], v[4:5]                    // 000000007050: 7CD60828
	v_mov_b32_e32 v1, 10                                       // 000000007054: 7E02028A
	s_and_saveexec_b64 s[40:41], vcc                           // 000000007058: BEA8206A
	s_cbranch_execz 9                                          // 00000000705C: BF880009 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x384>
	s_mov_b32 s42, 0xdf3b645b                                  // 000000007060: BEAA00FF DF3B645B
	s_mov_b32 s43, 0x3feb8d4f                                  // 000000007068: BEAB00FF 3FEB8D4F
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:325
	v_cmp_ngt_f64_e32 vcc, s[42:43], v[4:5]                    // 000000007070: 7CD6082A
	v_mov_b32_e32 v1, 11                                       // 000000007074: 7E02028B
	s_and_saveexec_b64 s[42:43], vcc                           // 000000007078: BEAA206A
	v_mov_b32_e32 v1, 0                                        // 00000000707C: 7E020280
	s_or_b64 exec, exec, s[42:43]                              // 000000007080: 87FE2A7E
	s_or_b64 exec, exec, s[40:41]                              // 000000007084: 87FE287E
	s_or_b64 exec, exec, s[38:39]                              // 000000007088: 87FE267E
	s_or_b64 exec, exec, s[36:37]                              // 00000000708C: 87FE247E
	s_or_b64 exec, exec, s[34:35]                              // 000000007090: 87FE227E
	s_or_b64 exec, exec, s[30:31]                              // 000000007094: 87FE1E7E
	s_or_b64 exec, exec, s[28:29]                              // 000000007098: 87FE1C7E
	s_or_b64 exec, exec, s[26:27]                              // 00000000709C: 87FE1A7E
	s_or_b64 exec, exec, s[24:25]                              // 0000000070A0: 87FE187E
	s_or_b64 exec, exec, s[2:3]                                // 0000000070A4: 87FE027E
	s_or_b64 exec, exec, s[0:1]                                // 0000000070A8: 87FE007E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:339
	v_cvt_f64_u32_e32 v[4:5], v3                               // 0000000070AC: 7E082D03
	v_ldexp_f64 v[4:5], v[4:5], 32                             // 0000000070B0: D2840004 00014104
	v_cvt_f64_u32_e32 v[2:3], v2                               // 0000000070B8: 7E042D02
	v_add_f64 v[2:3], v[4:5], v[2:3]                           // 0000000070BC: D2800002 00020504
	s_movk_i32 s0, 0xffc1                                      // 0000000070C4: B000FFC1
	s_waitcnt lgkmcnt(0)                                       // 0000000070C8: BF8CC07F
	s_cmp_lt_i32 s22, 2                                        // 0000000070CC: BF048216
	v_ldexp_f64 v[2:3], v[2:3], s0                             // 0000000070D0: D2840002 00000102
	s_cbranch_scc1 54                                          // 0000000070D8: BF850036 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x4b4>
	s_cmp_eq_u32 s22, 2                                        // 0000000070DC: BF068216
	v_mov_b64_e32 v[16:17], -1                                 // 0000000070E0: 7E2070C1
	s_cbranch_scc0 49                                          // 0000000070E4: BF840031 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x4ac>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:217
	v_cvt_f64_i32_e32 v[4:5], s23                              // 0000000070E8: 7E080817
	v_div_scale_f64 v[6:7], s[0:1], v[4:5], v[4:5], 1.0        // 0000000070EC: D1E10006 03CA0904
	v_rcp_f64_e32 v[8:9], v[6:7]                               // 0000000070F4: 7E104B06
	v_div_scale_f64 v[10:11], vcc, 1.0, v[4:5], 1.0            // 0000000070F8: D1E16A0A 03CA08F2
	v_fma_f64 v[12:13], -v[6:7], v[8:9], 1.0                   // 000000007100: D1CC000C 23CA1106
	v_fmac_f64_e32 v[8:9], v[8:9], v[12:13]                    // 000000007108: 08101908
	v_fma_f64 v[12:13], -v[6:7], v[8:9], 1.0                   // 00000000710C: D1CC000C 23CA1106
	v_fmac_f64_e32 v[8:9], v[8:9], v[12:13]                    // 000000007114: 08101908
	v_mul_f64 v[12:13], v[10:11], v[8:9]                       // 000000007118: D281000C 0002110A
	v_fma_f64 v[6:7], -v[6:7], v[12:13], v[10:11]              // 000000007120: D1CC0006 242A1906
	v_div_fmas_f64 v[6:7], v[6:7], v[8:9], v[12:13]            // 000000007128: D1E30006 04321106
	v_div_fixup_f64 v[4:5], v[6:7], v[4:5], 1.0                // 000000007130: D1DF0004 03CA0906
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:218
	v_div_scale_f64 v[6:7], s[0:1], v[4:5], v[4:5], v[2:3]     // 000000007138: D1E10006 040A0904
	v_rcp_f64_e32 v[8:9], v[6:7]                               // 000000007140: 7E104B06
	s_movk_i32 s0, 0xffe0                                      // 000000007144: B000FFE0
	v_fma_f64 v[10:11], -v[6:7], v[8:9], 1.0                   // 000000007148: D1CC000A 23CA1106
	v_fmac_f64_e32 v[8:9], v[8:9], v[10:11]                    // 000000007150: 08101508
	v_fma_f64 v[10:11], -v[6:7], v[8:9], 1.0                   // 000000007154: D1CC000A 23CA1106
	v_fmac_f64_e32 v[8:9], v[8:9], v[10:11]                    // 00000000715C: 08101508
	v_div_scale_f64 v[10:11], vcc, v[2:3], v[4:5], v[2:3]      // 000000007160: D1E16A0A 040A0902
	v_mul_f64 v[12:13], v[10:11], v[8:9]                       // 000000007168: D281000C 0002110A
	v_fma_f64 v[6:7], -v[6:7], v[12:13], v[10:11]              // 000000007170: D1CC0006 242A1906
	s_nop 1                                                    // 000000007178: BF800001
	v_div_fmas_f64 v[6:7], v[6:7], v[8:9], v[12:13]            // 00000000717C: D1E30006 04321106
	v_div_fixup_f64 v[4:5], v[6:7], v[4:5], v[2:3]             // 000000007184: D1DF0004 040A0906
	v_trunc_f64_e32 v[4:5], v[4:5]                             // 00000000718C: 7E082F04
	v_ldexp_f64 v[6:7], v[4:5], s0                             // 000000007190: D2840006 00000104
	v_floor_f64_e32 v[6:7], v[6:7]                             // 000000007198: 7E0C3506
	v_fmac_f64_e32 v[4:5], 0xc1f00000, v[6:7]                  // 00000000719C: 08080CFF C1F00000
	v_cvt_u32_f64_e32 v16, v[4:5]                              // 0000000071A4: 7E202B04
	v_cvt_i32_f64_e32 v17, v[6:7]                              // 0000000071A8: 7E220706
	s_cbranch_execz 1                                          // 0000000071AC: BF880001 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x4b4>
	s_branch 43                                                // 0000000071B0: BF82002B <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x560>
	s_cmp_lg_u32 s22, 0                                        // 0000000071B4: BF078016
	v_mov_b64_e32 v[16:17], -1                                 // 0000000071B8: 7E2070C1
	s_cbranch_scc1 40                                          // 0000000071BC: BF850028 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x560>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:214
	s_mul_i32 s0, s18, s17                                     // 0000000071C0: 92001112
	s_mul_hi_u32 s1, s18, s16                                  // 0000000071C4: 96011012
	s_add_i32 s0, s1, s0                                       // 0000000071C8: 81000001
	s_mul_i32 s1, s19, s16                                     // 0000000071CC: 92011013
	s_add_i32 s1, s0, s1                                       // 0000000071D0: 81010100
	s_mul_i32 s0, s18, s16                                     // 0000000071D4: 92001012
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:254
	v_cmp_lt_i64_e64 s[2:3], s[0:1], 3                         // 0000000071D8: D0E10002 00010600
	s_and_b64 vcc, exec, s[2:3]                                // 0000000071E0: 86EA027E
	v_mov_b64_e32 v[16:17], 0                                  // 0000000071E4: 7E207080
	s_cbranch_vccnz 29                                         // 0000000071E8: BF87001D <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x560>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:250
	s_add_u32 s2, s0, -1                                       // 0000000071EC: 8002C100
	s_addc_u32 s3, s1, -1                                      // 0000000071F0: 8203C101
	s_mov_b64 s[0:1], 0                                        // 0000000071F4: BE800180
	v_mov_b64_e32 v[6:7], s[2:3]                               // 0000000071F8: 7E0C7002
	v_mov_b64_e32 v[16:17], 0                                  // 0000000071FC: 7E207080
	v_mov_b64_e32 v[4:5], s[2:3]                               // 000000007200: 7E087002
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:256
	v_lshrrev_b64 v[6:7], 1, v[6:7]                            // 000000007204: D2900006 00020C81
	v_lshl_add_u64 v[6:7], v[16:17], 0, v[6:7]                 // 00000000720C: D2080006 04190110
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:258
	v_lshl_add_u64 v[8:9], v[6:7], 3, s[10:11]                 // 000000007214: D2080008 00290706
	global_load_dwordx2 v[8:9], v[8:9], off                    // 00000000721C: DC548000 087F0008
	s_waitcnt vmcnt(0)                                         // 000000007224: BF8C0F70
	v_cmp_gt_f64_e32 vcc, v[8:9], v[2:3]                       // 000000007228: 7CC80508
	s_nop 1                                                    // 00000000722C: BF800001
	v_cndmask_b32_e32 v16, v6, v16, vcc                        // 000000007230: 00202106
	v_cndmask_b32_e32 v4, v4, v6, vcc                          // 000000007234: 00080D04
	v_cndmask_b32_e32 v17, v7, v17, vcc                        // 000000007238: 00222307
	v_cndmask_b32_e32 v5, v5, v7, vcc                          // 00000000723C: 000A0F05
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:263
	v_sub_co_u32_e32 v6, vcc, v4, v16                          // 000000007240: 340C2104
	s_nop 1                                                    // 000000007244: BF800001
	v_subb_co_u32_e32 v7, vcc, v5, v17, vcc                    // 000000007248: 3A0E2305
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:254
	v_cmp_gt_i64_e32 vcc, 2, v[6:7]                            // 00000000724C: 7DC80C82
	s_or_b64 s[0:1], vcc, s[0:1]                               // 000000007250: 8780006A
	s_andn2_b64 exec, exec, s[0:1]                             // 000000007254: 89FE007E
	s_cbranch_execnz 65514                                     // 000000007258: BF89FFEA <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x504>
	s_or_b64 exec, exec, s[0:1]                                // 00000000725C: 87FE007E
	v_lshlrev_b32_e32 v4, 2, v1                                // 000000007260: 24080282
	global_load_dword v32, v4, s[4:5]                          // 000000007264: DC508000 20040004
	v_mov_b64_e32 v[4:5], 0                                    // 00000000726C: 7E087080
	s_mov_b32 s33, 0                                           // 000000007270: BEA10080
	v_mov_b64_e32 v[6:7], v[4:5]                               // 000000007274: 7E0C7104
	v_mov_b64_e32 v[8:9], v[4:5]                               // 000000007278: 7E107104
	v_mov_b64_e32 v[10:11], v[4:5]                             // 00000000727C: 7E147104
	v_mov_b64_e32 v[14:15], v[4:5]                             // 000000007280: 7E1C7104
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:231
	s_waitcnt vmcnt(0)                                         // 000000007284: BF8C0F70
	v_cmp_lt_i32_e32 vcc, 0, v32                               // 000000007288: 7D824080
	s_and_saveexec_b64 s[4:5], vcc                             // 00000000728C: BE84206A
	s_cbranch_execz 342                                        // 000000007290: BF880156 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xaec>
	v_mul_lo_u32 v33, v1, s44                                  // 000000007294: D2850021 00005901
	v_mul_lo_u32 v1, v17, s16                                  // 00000000729C: D2850001 00002111
	v_mul_lo_u32 v8, v16, s17                                  // 0000000072A4: D2850008 00002310
	v_mad_u64_u32 v[6:7], s[0:1], v16, s16, 0                  // 0000000072AC: D1E80006 02002110
	s_add_u32 s10, s18, -1                                     // 0000000072B4: 800AC112
	v_mov_b32_e32 v4, s12                                      // 0000000072B8: 7E08020C
	v_mov_b32_e32 v5, s13                                      // 0000000072BC: 7E0A020D
	v_add3_u32 v7, v7, v8, v1                                  // 0000000072C0: D1FF0007 04061107
	s_addc_u32 s11, s19, -1                                    // 0000000072C8: 820BC113
	s_add_i32 s0, s23, -1                                      // 0000000072CC: 8100C117
	v_lshl_add_u64 v[12:13], v[6:7], 2, v[4:5]                 // 0000000072D0: D208000C 04110506
	s_ashr_i32 s1, s0, 31                                      // 0000000072D8: 90019F00
	v_cmp_gt_i64_e64 s[2:3], s[18:19], 2                       // 0000000072DC: D0E40002 00010412
	v_cmp_ne_u64_e64 s[0:1], s[0:1], v[16:17]                  // 0000000072E4: D0ED0000 00022000
	v_lshl_add_u64 v[16:17], s[16:17], 2, v[12:13]             // 0000000072EC: D2080010 04310410
	v_mov_b64_e32 v[4:5], 0                                    // 0000000072F4: 7E087080
	v_cndmask_b32_e64 v1, 0, 1, s[2:3]                         // 0000000072F8: D1000001 00090280
	s_movk_i32 s16, 0xffa0                                     // 000000007300: B010FFA0
	s_add_i32 s23, s18, -1                                     // 000000007304: 8117C112
	s_mov_b64 s[12:13], 0                                      // 000000007308: BE8C0180
	v_cmp_ne_u32_e64 s[2:3], 1, v1                             // 00000000730C: D0CD0002 00020281
	s_mov_b32 s17, -1                                          // 000000007314: BE9100C1
	v_not_b32_e32 v34, 47                                      // 000000007318: 7E4456AF
	v_mov_b64_e32 v[6:7], v[4:5]                               // 00000000731C: 7E0C7104
	v_mov_b64_e32 v[8:9], v[4:5]                               // 000000007320: 7E107104
	v_mov_b64_e32 v[10:11], v[4:5]                             // 000000007324: 7E147104
	v_mov_b64_e32 v[14:15], v[4:5]                             // 000000007328: 7E1C7104
	s_branch 69                                                // 00000000732C: BF820045 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x744>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:174
	global_load_dwordx4 v[24:27], v[22:23], off offset:48      // 000000007330: DC5C8030 187F0016
	global_load_dwordx4 v[28:31], v[22:23], off                // 000000007338: DC5C8000 1C7F0016
	global_load_dwordx4 v[36:39], v[22:23], off offset:16      // 000000007340: DC5C8010 247F0016
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:180
	global_load_dwordx4 v[40:43], v[22:23], off offset:64      // 000000007348: DC5C8040 287F0016
	global_load_dwordx4 v[44:47], v[22:23], off offset:80      // 000000007350: DC5C8050 2C7F0016
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:174
	global_load_dwordx4 v[48:51], v[22:23], off offset:32      // 000000007358: DC5C8020 307F0016
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:231
	s_add_i32 s33, s33, 1                                      // 000000007360: 81218121
	v_cmp_eq_u32_e32 vcc, s33, v32                             // 000000007364: 7D944021
	s_or_b64 s[12:13], vcc, s[12:13]                           // 000000007368: 878C0C6A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:174
	s_waitcnt vmcnt(5)                                         // 00000000736C: BF8C0F75
	v_add_f64 v[20:21], v[24:25], -v[2:3]                      // 000000007370: D2800014 40020518
	s_waitcnt vmcnt(4)                                         // 000000007378: BF8C0F74
	v_add_f64 v[22:23], v[24:25], -v[28:29]                    // 00000000737C: D2800016 40023918
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:177
	v_add_f64 v[24:25], v[26:27], -v[30:31]                    // 000000007384: D2800018 40023D1A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:183
	s_waitcnt vmcnt(2)                                         // 00000000738C: BF8C0F72
	v_add_f64 v[30:31], v[42:43], -v[38:39]                    // 000000007390: D280001E 40024D2A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:174
	v_div_scale_f64 v[38:39], s[24:25], v[22:23], v[22:23], v[20:21]// 000000007398: D1E11826 04522D16
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:180
	v_add_f64 v[28:29], v[40:41], -v[36:37]                    // 0000000073A0: D280001C 40024928
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:186
	s_waitcnt vmcnt(0)                                         // 0000000073A8: BF8C0F70
	v_add_f64 v[36:37], v[44:45], -v[48:49]                    // 0000000073AC: D2800024 4002612C
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:174
	v_rcp_f64_e32 v[48:49], v[38:39]                           // 0000000073B4: 7E604B26
	v_div_scale_f64 v[52:53], vcc, v[20:21], v[22:23], v[20:21]// 0000000073B8: D1E16A34 04522D14
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:189
	v_add_f64 v[50:51], v[46:47], -v[50:51]                    // 0000000073C0: D2800032 4002652E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:174
	v_fma_f64 v[54:55], -v[38:39], v[48:49], 1.0               // 0000000073C8: D1CC0036 23CA6126
	v_fmac_f64_e32 v[48:49], v[48:49], v[54:55]                // 0000000073D0: 08606D30
	v_fma_f64 v[54:55], -v[38:39], v[48:49], 1.0               // 0000000073D4: D1CC0036 23CA6126
	v_fmac_f64_e32 v[48:49], v[48:49], v[54:55]                // 0000000073DC: 08606D30
	v_mul_f64 v[54:55], v[52:53], v[48:49]                     // 0000000073E0: D2810036 00026134
	v_fma_f64 v[38:39], -v[38:39], v[54:55], v[52:53]          // 0000000073E8: D1CC0026 24D26D26
	v_div_fmas_f64 v[38:39], v[38:39], v[48:49], v[54:55]      // 0000000073F0: D1E30026 04DA6126
	v_div_fixup_f64 v[20:21], v[38:39], v[22:23], v[20:21]     // 0000000073F8: D1DF0014 04522D26
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:177
	v_fma_f64 v[22:23], -v[20:21], v[24:25], v[26:27]          // 000000007400: D1CC0016 246A3114
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:180
	v_fma_f64 v[24:25], -v[20:21], v[28:29], v[40:41]          // 000000007408: D1CC0018 24A23914
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:183
	v_fma_f64 v[26:27], -v[20:21], v[30:31], v[42:43]          // 000000007410: D1CC001A 24AA3D14
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:186
	v_fma_f64 v[28:29], -v[20:21], v[36:37], v[44:45]          // 000000007418: D1CC001C 24B24914
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:189
	v_fma_f64 v[20:21], -v[20:21], v[50:51], v[46:47]          // 000000007420: D1CC0014 24BA6514
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:240
	v_fmac_f64_e32 v[14:15], v[18:19], v[22:23]                // 000000007428: 081C2D12
	v_fmac_f64_e32 v[10:11], v[18:19], v[24:25]                // 00000000742C: 08143112
	v_fmac_f64_e32 v[8:9], v[18:19], v[26:27]                  // 000000007430: 08103512
	v_fmac_f64_e32 v[6:7], v[18:19], v[28:29]                  // 000000007434: 080C3912
	v_fmac_f64_e32 v[4:5], v[18:19], v[20:21]                  // 000000007438: 08082912
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:231
	s_andn2_b64 exec, exec, s[12:13]                           // 00000000743C: 89FE0C7E
	s_cbranch_execz 233                                        // 000000007440: BF8800E9 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xae8>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:234
	v_add_u32_e32 v18, s33, v33                                // 000000007444: 68244221
	v_ashrrev_i32_e32 v19, 31, v18                             // 000000007448: 2226249F
	v_lshl_add_u64 v[20:21], v[18:19], 2, s[8:9]               // 00000000744C: D2080014 00210512
	global_load_dword v20, v[20:21], off                       // 000000007454: DC508000 147F0014
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:235
	v_lshl_add_u64 v[18:19], v[18:19], 3, s[6:7]               // 00000000745C: D2080012 00190712
	global_load_dwordx2 v[18:19], v[18:19], off                // 000000007464: DC548000 127F0012
	s_cmp_lt_i32 s22, 1                                        // 00000000746C: BF048116
	s_mov_b64 s[24:25], 0                                      // 000000007470: BE980180
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:234
	s_waitcnt vmcnt(1)                                         // 000000007474: BF8C0F71
	v_ashrrev_i32_e32 v21, 31, v20                             // 000000007478: 222A289F
	s_cbranch_scc1 63                                          // 00000000747C: BF85003F <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x87c>
	s_cmp_eq_u32 s22, 1                                        // 000000007480: BF068116
	s_cbranch_scc0 202                                         // 000000007484: BF8400CA <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xab0>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:122
	v_mul_lo_u32 v1, s19, v20                                  // 000000007488: D2850001 00022813
	v_mul_lo_u32 v24, s18, v21                                 // 000000007490: D2850018 00022A12
	v_mad_u64_u32 v[22:23], s[26:27], s18, v20, 0              // 000000007498: D1E81A16 02022812
	v_add3_u32 v1, v23, v24, v1                                // 0000000074A0: D1FF0001 04063117
	v_mad_u64_u32 v[24:25], s[26:27], v22, 48, s[14:15]        // 0000000074A8: D1E81A18 00396116
	v_mov_b32_e32 v22, v25                                     // 0000000074B0: 7E2C0319
	v_mad_u64_u32 v[22:23], s[26:27], v1, 48, v[22:23]         // 0000000074B4: D1E81A16 04596101
	v_mov_b32_e32 v25, v22                                     // 0000000074BC: 7E320316
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:277
	s_and_b64 vcc, exec, s[2:3]                                // 0000000074C0: 86EA027E
	v_mov_b64_e32 v[26:27], 0                                  // 0000000074C4: 7E347080
	s_cbranch_vccnz 31                                         // 0000000074C8: BF87001F <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x848>
	s_mov_b64 s[26:27], 0                                      // 0000000074CC: BE9A0180
	v_mov_b64_e32 v[28:29], s[10:11]                           // 0000000074D0: 7E38700A
	v_mov_b64_e32 v[26:27], 0                                  // 0000000074D4: 7E347080
	v_mov_b64_e32 v[22:23], s[10:11]                           // 0000000074D8: 7E2C700A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:279
	v_lshrrev_b64 v[28:29], 1, v[28:29]                        // 0000000074DC: D290001C 00023881
	v_lshl_add_u64 v[28:29], v[26:27], 0, v[28:29]             // 0000000074E4: D208001C 0471011A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:281
	v_mad_u64_u32 v[30:31], s[28:29], v28, 48, v[24:25]        // 0000000074EC: D1E81C1E 0461611C
	v_mov_b32_e32 v36, v31                                     // 0000000074F4: 7E48031F
	v_mad_u64_u32 v[36:37], s[28:29], v29, 48, v[36:37]        // 0000000074F8: D1E81C24 0491611D
	v_mov_b32_e32 v31, v36                                     // 000000007500: 7E3E0324
	global_load_dwordx2 v[30:31], v[30:31], off                // 000000007504: DC548000 1E7F001E
	s_waitcnt vmcnt(0)                                         // 00000000750C: BF8C0F70
	v_cmp_gt_f64_e32 vcc, v[30:31], v[2:3]                     // 000000007510: 7CC8051E
	s_nop 1                                                    // 000000007514: BF800001
	v_cndmask_b32_e32 v26, v28, v26, vcc                       // 000000007518: 0034351C
	v_cndmask_b32_e32 v22, v22, v28, vcc                       // 00000000751C: 002C3916
	v_cndmask_b32_e32 v27, v29, v27, vcc                       // 000000007520: 0036371D
	v_cndmask_b32_e32 v23, v23, v29, vcc                       // 000000007524: 002E3B17
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:286
	v_sub_co_u32_e32 v28, vcc, v22, v26                        // 000000007528: 34383516
	s_nop 1                                                    // 00000000752C: BF800001
	v_subb_co_u32_e32 v29, vcc, v23, v27, vcc                  // 000000007530: 3A3A3717
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:277
	v_cmp_gt_i64_e32 vcc, 2, v[28:29]                          // 000000007534: 7DC83882
	s_or_b64 s[26:27], vcc, s[26:27]                           // 000000007538: 879A1A6A
	s_andn2_b64 exec, exec, s[26:27]                           // 00000000753C: 89FE1A7E
	s_cbranch_execnz 65510                                     // 000000007540: BF89FFE6 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x7dc>
	s_or_b64 exec, exec, s[26:27]                              // 000000007544: 87FE1A7E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:126
	v_cmp_ne_u64_e32 vcc, s[10:11], v[26:27]                   // 000000007548: 7DDA340A
	s_and_saveexec_b64 s[26:27], vcc                           // 00000000754C: BE9A206A
	s_xor_b64 s[26:27], exec, s[26:27]                         // 000000007550: 889A1A7E
	s_cbranch_execz 152                                        // 000000007554: BF880098 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xab8>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:129
	v_mad_u64_u32 v[22:23], s[28:29], v26, 48, v[24:25]        // 000000007558: D1E81C16 0461611A
	v_mov_b32_e32 v24, v23                                     // 000000007560: 7E300317
	v_mad_u64_u32 v[24:25], s[28:29], v27, 48, v[24:25]        // 000000007564: D1E81C18 0461611B
	v_mov_b32_e32 v23, v24                                     // 00000000756C: 7E2E0318
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:126
	s_andn2_saveexec_b64 s[26:27], s[26:27]                    // 000000007570: BE9A231A
	s_cbranch_execnz 145                                       // 000000007574: BF890091 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xabc>
	s_branch 152                                               // 000000007578: BF820098 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xadc>
	s_mov_b64 s[26:27], 0                                      // 00000000757C: BE9A0180
	s_cbranch_execz 3                                          // 000000007580: BF880003 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x890>
	s_cmp_lg_u32 s22, 0                                        // 000000007584: BF078016
	s_mov_b64 s[24:25], -1                                     // 000000007588: BE9801C1
	s_cselect_b64 s[26:27], -1, 0                              // 00000000758C: 859A80C1
	s_andn2_b64 vcc, exec, s[26:27]                            // 000000007590: 89EA1A7E
	v_lshl_add_u64 v[24:25], v[20:21], 2, v[12:13]             // 000000007594: D2080018 04310514
	s_cbranch_vccnz 102                                        // 00000000759C: BF870066 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0xa38>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:143
	global_load_dword v22, v[24:25], off                       // 0000000075A0: DC508000 167F0018
	v_mov_b32_e32 v28, s23                                     // 0000000075A8: 7E380217
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:147
	s_and_saveexec_b64 s[24:25], s[0:1]                        // 0000000075AC: BE982000
	s_cbranch_execz 6                                          // 0000000075B0: BF880006 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x8cc>
	v_lshl_add_u64 v[26:27], v[20:21], 2, v[16:17]             // 0000000075B4: D208001A 04410514
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:150
	global_load_dword v1, v[26:27], off                        // 0000000075BC: DC508000 017F001A
	s_waitcnt vmcnt(0)                                         // 0000000075C4: BF8C0F70
	v_add_u32_e32 v28, 1, v1                                   // 0000000075C8: 68380281
	s_or_b64 exec, exec, s[24:25]                              // 0000000075CC: 87FE187E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:155
	v_mul_lo_u32 v1, s19, v20                                  // 0000000075D0: D2850001 00022813
	v_mul_lo_u32 v23, s18, v21                                 // 0000000075D8: D2850017 00022A12
	v_mad_u64_u32 v[26:27], s[24:25], s18, v20, 0              // 0000000075E0: D1E8181A 02022812
	v_add3_u32 v1, v27, v23, v1                                // 0000000075E8: D1FF0001 04062F1B
	v_mad_u64_u32 v[26:27], s[24:25], v26, 48, s[14:15]        // 0000000075F0: D1E8181A 0039611A
	v_mov_b32_e32 v30, v27                                     // 0000000075F8: 7E3C031B
	v_mad_u64_u32 v[30:31], s[24:25], v1, 48, v[30:31]         // 0000000075FC: D1E8181E 04796101
	v_mov_b32_e32 v27, v30                                     // 000000007604: 7E36031E
	s_waitcnt vmcnt(0)                                         // 000000007608: BF8C0F70
	v_mad_i64_i32 v[30:31], s[24:25], v22, 48, v[26:27]        // 00000000760C: D1E9181E 04696116
	global_load_dwordx2 v[30:31], v[30:31], off                // 000000007614: DC548000 1E7F001E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:158
	s_waitcnt vmcnt(0)                                         // 00000000761C: BF8C0F70
	v_cmp_nge_f64_e32 vcc, v[30:31], v[2:3]                    // 000000007620: 7CD2051E
	v_mov_b64_e32 v[30:31], 0                                  // 000000007624: 7E3C7080
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:158
	s_and_saveexec_b64 s[24:25], vcc                           // 000000007628: BE98206A
	s_cbranch_execz 48                                         // 00000000762C: BF880030 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x9f0>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:156
	v_mad_i64_i32 v[30:31], s[26:27], v28, 48, v[26:27]        // 000000007630: D1E91A1E 0469611C
	global_load_dwordx2 v[30:31], v[30:31], off                // 000000007638: DC548000 1E7F001E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:160
	s_waitcnt vmcnt(0)                                         // 000000007640: BF8C0F70
	v_cmp_nle_f64_e32 vcc, v[30:31], v[2:3]                    // 000000007644: 7CD8051E
	v_mov_b64_e32 v[30:31], s[10:11]                           // 000000007648: 7E3C700A
	s_and_saveexec_b64 s[26:27], vcc                           // 00000000764C: BE9A206A
	s_cbranch_execz 38                                         // 000000007650: BF880026 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x9ec>
	v_ashrrev_i32_e32 v23, 31, v22                             // 000000007654: 222E2C9F
	v_ashrrev_i32_e32 v1, 31, v28                              // 000000007658: 2202389F
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:275
	v_sub_co_u32_e32 v30, vcc, v28, v22                        // 00000000765C: 343C2D1C
	s_nop 1                                                    // 000000007660: BF800001
	v_subb_co_u32_e32 v31, vcc, v1, v23, vcc                   // 000000007664: 3A3E2F01
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:277
	v_cmp_lt_i64_e32 vcc, 1, v[30:31]                          // 000000007668: 7DC23C81
	s_and_saveexec_b64 s[28:29], vcc                           // 00000000766C: BE9C206A
	s_cbranch_execz 28                                         // 000000007670: BF88001C <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x9e4>
	s_mov_b64 s[30:31], 0                                      // 000000007674: BE9E0180
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:279
	v_lshrrev_b64 v[30:31], 1, v[30:31]                        // 000000007678: D290001E 00023C81
	v_lshl_add_u64 v[30:31], v[22:23], 0, v[30:31]             // 000000007680: D208001E 04790116
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:281
	v_mad_u64_u32 v[36:37], s[34:35], v30, 48, v[26:27]        // 000000007688: D1E82224 0469611E
	v_mov_b32_e32 v38, v37                                     // 000000007690: 7E4C0325
	v_mad_u64_u32 v[38:39], s[34:35], v31, 48, v[38:39]        // 000000007694: D1E82226 0499611F
	v_mov_b32_e32 v37, v38                                     // 00000000769C: 7E4A0326
	global_load_dwordx2 v[36:37], v[36:37], off                // 0000000076A0: DC548000 247F0024
	s_waitcnt vmcnt(0)                                         // 0000000076A8: BF8C0F70
	v_cmp_gt_f64_e32 vcc, v[36:37], v[2:3]                     // 0000000076AC: 7CC80524
	s_nop 1                                                    // 0000000076B0: BF800001
	v_cndmask_b32_e32 v22, v30, v22, vcc                       // 0000000076B4: 002C2D1E
	v_cndmask_b32_e32 v28, v28, v30, vcc                       // 0000000076B8: 00383D1C
	v_cndmask_b32_e32 v23, v31, v23, vcc                       // 0000000076BC: 002E2F1F
	v_cndmask_b32_e32 v1, v1, v31, vcc                         // 0000000076C0: 00023F01
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:286
	v_sub_co_u32_e32 v30, vcc, v28, v22                        // 0000000076C4: 343C2D1C
	s_nop 1                                                    // 0000000076C8: BF800001
	v_subb_co_u32_e32 v31, vcc, v1, v23, vcc                   // 0000000076CC: 3A3E2F01
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:277
	v_cmp_gt_i64_e32 vcc, 2, v[30:31]                          // 0000000076D0: 7DC83C82
	s_or_b64 s[30:31], vcc, s[30:31]                           // 0000000076D4: 879E1E6A
	s_andn2_b64 exec, exec, s[30:31]                           // 0000000076D8: 89FE1E7E
	s_cbranch_execnz 65510                                     // 0000000076DC: BF89FFE6 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x978>
	s_or_b64 exec, exec, s[30:31]                              // 0000000076E0: 87FE1E7E
	s_or_b64 exec, exec, s[28:29]                              // 0000000076E4: 87FE1C7E
	v_mov_b64_e32 v[30:31], v[22:23]                           // 0000000076E8: 7E3C7116
	s_or_b64 exec, exec, s[26:27]                              // 0000000076EC: 87FE1A7E
	s_or_b64 exec, exec, s[24:25]                              // 0000000076F0: 87FE187E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:165
	v_ashrrev_i32_e32 v31, 31, v30                             // 0000000076F4: 223E3C9F
	v_cmp_ne_u64_e32 vcc, s[10:11], v[30:31]                   // 0000000076F8: 7DDA3C0A
	s_and_saveexec_b64 s[24:25], vcc                           // 0000000076FC: BE98206A
	s_xor_b64 s[24:25], exec, s[24:25]                         // 000000007700: 8898187E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:168
	v_mad_i64_i32 v[22:23], s[26:27], v30, 48, v[26:27]        // 000000007704: D1E91A16 0469611E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:165
	s_andn2_saveexec_b64 s[24:25], s[24:25]                    // 00000000770C: BE982318
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:166
	v_mad_u64_u32 v[22:23], s[26:27], s18, 48, v[26:27]        // 000000007710: D1E81A16 04696012
	v_mov_b32_e32 v26, v23                                     // 000000007718: 7E340317
	v_mad_u64_u32 v[26:27], s[26:27], s19, 48, v[26:27]        // 00000000771C: D1E81A1A 04696013
	v_mov_b32_e32 v23, v26                                     // 000000007724: 7E2E031A
	v_lshl_add_u64 v[22:23], v[22:23], 0, s[16:17]             // 000000007728: D2080016 00410116
	s_or_b64 exec, exec, s[24:25]                              // 000000007730: 87FE187E
	s_branch 65278                                             // 000000007734: BF82FEFE <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x630>
	s_and_b64 vcc, exec, s[24:25]                              // 000000007738: 86EA187E
	s_cbranch_vccz 65276                                       // 00000000773C: BF86FEFC <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x630>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:135
	global_load_dword v22, v[24:25], off                       // 000000007740: DC508000 167F0018
	v_mul_lo_u32 v1, s19, v20                                  // 000000007748: D2850001 00022813
	v_mul_lo_u32 v23, s18, v21                                 // 000000007750: D2850017 00022A12
	v_mad_u64_u32 v[20:21], s[24:25], s18, v20, 0              // 000000007758: D1E81814 02022812
	v_add3_u32 v1, v21, v23, v1                                // 000000007760: D1FF0001 04062F15
	v_mad_u64_u32 v[20:21], s[24:25], v20, 48, s[14:15]        // 000000007768: D1E81814 00396114
	v_mov_b32_e32 v24, v21                                     // 000000007770: 7E300315
	v_mad_u64_u32 v[24:25], s[24:25], v1, 48, v[24:25]         // 000000007774: D1E81818 04616101
	v_mov_b32_e32 v21, v24                                     // 00000000777C: 7E2A0318
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:135
	s_waitcnt vmcnt(0)                                         // 000000007780: BF8C0F70
	v_ashrrev_i32_e32 v23, 31, v22                             // 000000007784: 222E2C9F
	v_cmp_eq_u64_e32 vcc, s[10:11], v[22:23]                   // 000000007788: 7DD42C0A
	v_mad_i64_i32 v[20:21], s[24:25], v22, 48, v[20:21]        // 00000000778C: D1E91814 04516116
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:135
	s_nop 0                                                    // 000000007794: BF800000
	v_cndmask_b32_e64 v23, 0, -1, vcc                          // 000000007798: D1000017 01A98280
	v_cndmask_b32_e32 v22, 0, v34, vcc                         // 0000000077A0: 002C4480
	v_lshl_add_u64 v[22:23], v[20:21], 0, v[22:23]             // 0000000077A4: D2080016 04590114
	s_branch 65248                                             // 0000000077AC: BF82FEE0 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x630>
	s_mov_b64 s[26:27], -1                                     // 0000000077B0: BE9A01C1
	s_branch 65398                                             // 0000000077B4: BF82FF76 <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x890>
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:126
	s_andn2_saveexec_b64 s[26:27], s[26:27]                    // 0000000077B8: BE9A231A
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:127
	v_mad_u64_u32 v[22:23], s[28:29], s18, 48, v[24:25]        // 0000000077BC: D1E81C16 04616012
	v_mov_b32_e32 v24, v23                                     // 0000000077C4: 7E300317
	v_mad_u64_u32 v[24:25], s[28:29], s19, 48, v[24:25]        // 0000000077C8: D1E81C18 04616013
	v_mov_b32_e32 v23, v24                                     // 0000000077D0: 7E2E0318
	v_lshl_add_u64 v[22:23], v[22:23], 0, s[16:17]             // 0000000077D4: D2080016 00410116
	s_or_b64 exec, exec, s[26:27]                              // 0000000077DC: 87FE1A7E
	s_mov_b64 s[26:27], 0                                      // 0000000077E0: BE9A0180
	s_branch 65386                                             // 0000000077E4: BF82FF6A <_Z25xs_lookup_kernel_baseline6Inputs14SimulationData+0x890>
	s_or_b64 exec, exec, s[12:13]                              // 0000000077E8: 87FE0C7E
	s_or_b64 exec, exec, s[4:5]                                // 0000000077EC: 87FE047E
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:98
	v_max_f64 v[2:3], v[14:15], v[14:15]                       // 0000000077F0: D2830002 00021D0E
	v_max_f64 v[2:3], v[2:3], -1.0                             // 0000000077F8: D2830002 0001E702
	v_cmp_gt_f64_e32 vcc, v[10:11], v[2:3]                     // 000000007800: 7CC8050A
	s_nop 1                                                    // 000000007804: BF800001
	v_cndmask_b32_e32 v3, v3, v11, vcc                         // 000000007808: 00061703
	v_cndmask_b32_e32 v2, v2, v10, vcc                         // 00000000780C: 00041502
	v_cmp_gt_f64_e64 s[0:1], v[8:9], v[2:3]                    // 000000007810: D0640000 00020508
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:104
	v_cndmask_b32_e64 v1, 1, 2, vcc                            // 000000007818: D1000001 01A90481
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:98
	s_nop 0                                                    // 000000007820: BF800000
	v_cndmask_b32_e64 v3, v3, v9, s[0:1]                       // 000000007824: D1000003 00021303
	v_cndmask_b32_e64 v2, v2, v8, s[0:1]                       // 00000000782C: D1000002 00021102
	v_cmp_gt_f64_e64 s[2:3], v[6:7], v[2:3]                    // 000000007834: D0640002 00020506
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:104
	v_cndmask_b32_e64 v1, v1, 3, s[0:1]                        // 00000000783C: D1000001 00010701
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:98
	s_nop 0                                                    // 000000007844: BF800000
	v_cndmask_b32_e64 v3, v3, v7, s[2:3]                       // 000000007848: D1000003 000A0F03
	v_cndmask_b32_e64 v2, v2, v6, s[2:3]                       // 000000007850: D1000002 000A0D02
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:104
	v_cndmask_b32_e64 v1, v1, 4, s[2:3]                        // 000000007858: D1000001 00090901
	v_cmp_ngt_f64_e32 vcc, v[4:5], v[2:3]                      // 000000007860: 7CD60504
	v_mov_b32_e32 v3, 0                                        // 000000007864: 7E060280
	s_nop 0                                                    // 000000007868: BF800000
	v_cndmask_b32_e32 v2, 5, v1, vcc                           // 00000000786C: 00040285
	v_ashrrev_i32_e32 v1, 31, v0                               // 000000007870: 2202009F
	v_lshl_add_u64 v[0:1], v[0:1], 3, s[20:21]                 // 000000007874: D2080000 00510700
	global_store_dwordx2 v[0:1], v[2:3], off                   // 00000000787C: DC748000 007F0200
; /p/vast1/fink12/claude-scratch/findingmnemo/xsbench-pr1/XSBench/hip/Simulation.cpp:105
	s_endpgm                                                   // 000000007884: BF810000
	s_nop 0                                                    // 000000007888: BF800000
	s_nop 0                                                    // 00000000788C: BF800000
	s_nop 0                                                    // 000000007890: BF800000
	s_nop 0                                                    // 000000007894: BF800000
	s_nop 0                                                    // 000000007898: BF800000
	s_nop 0                                                    // 00000000789C: BF800000
	s_nop 0                                                    // 0000000078A0: BF800000
	s_nop 0                                                    // 0000000078A4: BF800000
	s_nop 0                                                    // 0000000078A8: BF800000
	s_nop 0                                                    // 0000000078AC: BF800000
	s_nop 0                                                    // 0000000078B0: BF800000
	s_nop 0                                                    // 0000000078B4: BF800000
	s_nop 0                                                    // 0000000078B8: BF800000
	s_nop 0                                                    // 0000000078BC: BF800000
	s_nop 0                                                    // 0000000078C0: BF800000
	s_nop 0                                                    // 0000000078C4: BF800000
	s_nop 0                                                    // 0000000078C8: BF800000
	s_nop 0                                                    // 0000000078CC: BF800000
	s_nop 0                                                    // 0000000078D0: BF800000
	s_nop 0                                                    // 0000000078D4: BF800000
	s_nop 0                                                    // 0000000078D8: BF800000
	s_nop 0                                                    // 0000000078DC: BF800000
	s_nop 0                                                    // 0000000078E0: BF800000
	s_nop 0                                                    // 0000000078E4: BF800000
	s_nop 0                                                    // 0000000078E8: BF800000
	s_nop 0                                                    // 0000000078EC: BF800000
	s_nop 0                                                    // 0000000078F0: BF800000
	s_nop 0                                                    // 0000000078F4: BF800000
	s_nop 0                                                    // 0000000078F8: BF800000
	s_nop 0                                                    // 0000000078FC: BF800000
	s_nop 0                                                    // 000000007900: BF800000
	s_nop 0                                                    // 000000007904: BF800000
	s_nop 0                                                    // 000000007908: BF800000
	s_nop 0                                                    // 00000000790C: BF800000
	s_nop 0                                                    // 000000007910: BF800000
	s_nop 0                                                    // 000000007914: BF800000
	s_nop 0                                                    // 000000007918: BF800000
	s_nop 0                                                    // 00000000791C: BF800000
	s_nop 0                                                    // 000000007920: BF800000
	s_nop 0                                                    // 000000007924: BF800000
	s_nop 0                                                    // 000000007928: BF800000
	s_nop 0                                                    // 00000000792C: BF800000
	s_nop 0                                                    // 000000007930: BF800000
	s_nop 0                                                    // 000000007934: BF800000
	s_nop 0                                                    // 000000007938: BF800000
	s_nop 0                                                    // 00000000793C: BF800000
	s_nop 0                                                    // 000000007940: BF800000
	s_nop 0                                                    // 000000007944: BF800000
	s_nop 0                                                    // 000000007948: BF800000
	s_nop 0                                                    // 00000000794C: BF800000
	s_nop 0                                                    // 000000007950: BF800000
	s_nop 0                                                    // 000000007954: BF800000
	s_nop 0                                                    // 000000007958: BF800000
	s_nop 0                                                    // 00000000795C: BF800000
	s_nop 0                                                    // 000000007960: BF800000
	s_nop 0                                                    // 000000007964: BF800000
	s_nop 0                                                    // 000000007968: BF800000
	s_nop 0                                                    // 00000000796C: BF800000
	s_nop 0                                                    // 000000007970: BF800000
	s_nop 0                                                    // 000000007974: BF800000
	s_nop 0                                                    // 000000007978: BF800000
	s_nop 0                                                    // 00000000797C: BF800000
	s_nop 0                                                    // 000000007980: BF800000
	s_nop 0                                                    // 000000007984: BF800000
	s_nop 0                                                    // 000000007988: BF800000
	s_nop 0                                                    // 00000000798C: BF800000
	s_nop 0                                                    // 000000007990: BF800000
	s_nop 0                                                    // 000000007994: BF800000
	s_nop 0                                                    // 000000007998: BF800000
	s_nop 0                                                    // 00000000799C: BF800000
	s_nop 0                                                    // 0000000079A0: BF800000
	s_nop 0                                                    // 0000000079A4: BF800000
	s_nop 0                                                    // 0000000079A8: BF800000
	s_nop 0                                                    // 0000000079AC: BF800000
	s_nop 0                                                    // 0000000079B0: BF800000
	s_nop 0                                                    // 0000000079B4: BF800000
	s_nop 0                                                    // 0000000079B8: BF800000
	s_nop 0                                                    // 0000000079BC: BF800000
	s_nop 0                                                    // 0000000079C0: BF800000
	s_nop 0                                                    // 0000000079C4: BF800000
	s_nop 0                                                    // 0000000079C8: BF800000
	s_nop 0                                                    // 0000000079CC: BF800000
	s_nop 0                                                    // 0000000079D0: BF800000
	s_nop 0                                                    // 0000000079D4: BF800000
	s_nop 0                                                    // 0000000079D8: BF800000
	s_nop 0                                                    // 0000000079DC: BF800000
	s_nop 0                                                    // 0000000079E0: BF800000
	s_nop 0                                                    // 0000000079E4: BF800000
	s_nop 0                                                    // 0000000079E8: BF800000
	s_nop 0                                                    // 0000000079EC: BF800000
	s_nop 0                                                    // 0000000079F0: BF800000
	s_nop 0                                                    // 0000000079F4: BF800000
	s_nop 0                                                    // 0000000079F8: BF800000
	s_nop 0                                                    // 0000000079FC: BF800000
	s_nop 0                                                    // 000000007A00: BF800000
	s_nop 0                                                    // 000000007A04: BF800000
	s_nop 0                                                    // 000000007A08: BF800000
	s_nop 0                                                    // 000000007A0C: BF800000
	s_nop 0                                                    // 000000007A10: BF800000
	s_nop 0                                                    // 000000007A14: BF800000
	s_nop 0                                                    // 000000007A18: BF800000
	s_nop 0                                                    // 000000007A1C: BF800000
	s_nop 0                                                    // 000000007A20: BF800000
	s_nop 0                                                    // 000000007A24: BF800000
	s_nop 0                                                    // 000000007A28: BF800000
	s_nop 0                                                    // 000000007A2C: BF800000
	s_nop 0                                                    // 000000007A30: BF800000
	s_nop 0                                                    // 000000007A34: BF800000
	s_nop 0                                                    // 000000007A38: BF800000
	s_nop 0                                                    // 000000007A3C: BF800000
	s_nop 0                                                    // 000000007A40: BF800000
	s_nop 0                                                    // 000000007A44: BF800000
	s_nop 0                                                    // 000000007A48: BF800000
	s_nop 0                                                    // 000000007A4C: BF800000
	s_nop 0                                                    // 000000007A50: BF800000
	s_nop 0                                                    // 000000007A54: BF800000
	s_nop 0                                                    // 000000007A58: BF800000
	s_nop 0                                                    // 000000007A5C: BF800000
	s_nop 0                                                    // 000000007A60: BF800000
	s_nop 0                                                    // 000000007A64: BF800000
	s_nop 0                                                    // 000000007A68: BF800000
	s_nop 0                                                    // 000000007A6C: BF800000
	s_nop 0                                                    // 000000007A70: BF800000
	s_nop 0                                                    // 000000007A74: BF800000
	s_nop 0                                                    // 000000007A78: BF800000
	s_nop 0                                                    // 000000007A7C: BF800000
	s_nop 0                                                    // 000000007A80: BF800000
	s_nop 0                                                    // 000000007A84: BF800000
	s_nop 0                                                    // 000000007A88: BF800000
	s_nop 0                                                    // 000000007A8C: BF800000
	s_nop 0                                                    // 000000007A90: BF800000
	s_nop 0                                                    // 000000007A94: BF800000
	s_nop 0                                                    // 000000007A98: BF800000
	s_nop 0                                                    // 000000007A9C: BF800000
	s_nop 0                                                    // 000000007AA0: BF800000
	s_nop 0                                                    // 000000007AA4: BF800000
	s_nop 0                                                    // 000000007AA8: BF800000
	s_nop 0                                                    // 000000007AAC: BF800000
	s_nop 0                                                    // 000000007AB0: BF800000
	s_nop 0                                                    // 000000007AB4: BF800000
	s_nop 0                                                    // 000000007AB8: BF800000
	s_nop 0                                                    // 000000007ABC: BF800000
	s_nop 0                                                    // 000000007AC0: BF800000
	s_nop 0                                                    // 000000007AC4: BF800000
	s_nop 0                                                    // 000000007AC8: BF800000
	s_nop 0                                                    // 000000007ACC: BF800000
	s_nop 0                                                    // 000000007AD0: BF800000
	s_nop 0                                                    // 000000007AD4: BF800000
	s_nop 0                                                    // 000000007AD8: BF800000
	s_nop 0                                                    // 000000007ADC: BF800000
	s_nop 0                                                    // 000000007AE0: BF800000
	s_nop 0                                                    // 000000007AE4: BF800000
	s_nop 0                                                    // 000000007AE8: BF800000
	s_nop 0                                                    // 000000007AEC: BF800000
	s_nop 0                                                    // 000000007AF0: BF800000
	s_nop 0                                                    // 000000007AF4: BF800000
	s_nop 0                                                    // 000000007AF8: BF800000
	s_nop 0                                                    // 000000007AFC: BF800000
	s_nop 0                                                    // 000000007B00: BF800000
	s_nop 0                                                    // 000000007B04: BF800000
	s_nop 0                                                    // 000000007B08: BF800000
	s_nop 0                                                    // 000000007B0C: BF800000
	s_nop 0                                                    // 000000007B10: BF800000
	s_nop 0                                                    // 000000007B14: BF800000
	s_nop 0                                                    // 000000007B18: BF800000
	s_nop 0                                                    // 000000007B1C: BF800000
	s_nop 0                                                    // 000000007B20: BF800000
	s_nop 0                                                    // 000000007B24: BF800000
	s_nop 0                                                    // 000000007B28: BF800000
	s_nop 0                                                    // 000000007B2C: BF800000
	s_nop 0                                                    // 000000007B30: BF800000
	s_nop 0                                                    // 000000007B34: BF800000
	s_nop 0                                                    // 000000007B38: BF800000
	s_nop 0                                                    // 000000007B3C: BF800000
	s_nop 0                                                    // 000000007B40: BF800000
	s_nop 0                                                    // 000000007B44: BF800000
	s_nop 0                                                    // 000000007B48: BF800000
	s_nop 0                                                    // 000000007B4C: BF800000
	s_nop 0                                                    // 000000007B50: BF800000
	s_nop 0                                                    // 000000007B54: BF800000
	s_nop 0                                                    // 000000007B58: BF800000
	s_nop 0                                                    // 000000007B5C: BF800000
	s_nop 0                                                    // 000000007B60: BF800000
	s_nop 0                                                    // 000000007B64: BF800000
	s_nop 0                                                    // 000000007B68: BF800000
	s_nop 0                                                    // 000000007B6C: BF800000
	s_nop 0                                                    // 000000007B70: BF800000
	s_nop 0                                                    // 000000007B74: BF800000
	s_nop 0                                                    // 000000007B78: BF800000
	s_nop 0                                                    // 000000007B7C: BF800000
	s_nop 0                                                    // 000000007B80: BF800000
	s_nop 0                                                    // 000000007B84: BF800000
	s_nop 0                                                    // 000000007B88: BF800000
	s_nop 0                                                    // 000000007B8C: BF800000
	s_nop 0                                                    // 000000007B90: BF800000
	s_nop 0                                                    // 000000007B94: BF800000
	s_nop 0                                                    // 000000007B98: BF800000
	s_nop 0                                                    // 000000007B9C: BF800000
	s_nop 0                                                    // 000000007BA0: BF800000
	s_nop 0                                                    // 000000007BA4: BF800000
	s_nop 0                                                    // 000000007BA8: BF800000
	s_nop 0                                                    // 000000007BAC: BF800000
	s_nop 0                                                    // 000000007BB0: BF800000
	s_nop 0                                                    // 000000007BB4: BF800000
	s_nop 0                                                    // 000000007BB8: BF800000
	s_nop 0                                                    // 000000007BBC: BF800000
	s_nop 0                                                    // 000000007BC0: BF800000
	s_nop 0                                                    // 000000007BC4: BF800000
	s_nop 0                                                    // 000000007BC8: BF800000
	s_nop 0                                                    // 000000007BCC: BF800000
	s_nop 0                                                    // 000000007BD0: BF800000
	s_nop 0                                                    // 000000007BD4: BF800000
	s_nop 0                                                    // 000000007BD8: BF800000
	s_nop 0                                                    // 000000007BDC: BF800000
	s_nop 0                                                    // 000000007BE0: BF800000
	s_nop 0                                                    // 000000007BE4: BF800000
	s_nop 0                                                    // 000000007BE8: BF800000
	s_nop 0                                                    // 000000007BEC: BF800000
	s_nop 0                                                    // 000000007BF0: BF800000
	s_nop 0                                                    // 000000007BF4: BF800000
	s_nop 0                                                    // 000000007BF8: BF800000
	s_nop 0                                                    // 000000007BFC: BF800000
	s_nop 0                                                    // 000000007C00: BF800000
	s_nop 0                                                    // 000000007C04: BF800000
	s_nop 0                                                    // 000000007C08: BF800000
	s_nop 0                                                    // 000000007C0C: BF800000
	s_nop 0                                                    // 000000007C10: BF800000
	s_nop 0                                                    // 000000007C14: BF800000
	s_nop 0                                                    // 000000007C18: BF800000
	s_nop 0                                                    // 000000007C1C: BF800000
	s_nop 0                                                    // 000000007C20: BF800000
	s_nop 0                                                    // 000000007C24: BF800000
	s_nop 0                                                    // 000000007C28: BF800000
	s_nop 0                                                    // 000000007C2C: BF800000
	s_nop 0                                                    // 000000007C30: BF800000
	s_nop 0                                                    // 000000007C34: BF800000
	s_nop 0                                                    // 000000007C38: BF800000
	s_nop 0                                                    // 000000007C3C: BF800000
	s_nop 0                                                    // 000000007C40: BF800000
	s_nop 0                                                    // 000000007C44: BF800000
	s_nop 0                                                    // 000000007C48: BF800000
	s_nop 0                                                    // 000000007C4C: BF800000
	s_nop 0                                                    // 000000007C50: BF800000
	s_nop 0                                                    // 000000007C54: BF800000
	s_nop 0                                                    // 000000007C58: BF800000
	s_nop 0                                                    // 000000007C5C: BF800000
	s_nop 0                                                    // 000000007C60: BF800000
	s_nop 0                                                    // 000000007C64: BF800000
	s_nop 0                                                    // 000000007C68: BF800000
	s_nop 0                                                    // 000000007C6C: BF800000
	s_nop 0                                                    // 000000007C70: BF800000
	s_nop 0                                                    // 000000007C74: BF800000
	s_nop 0                                                    // 000000007C78: BF800000
	s_nop 0                                                    // 000000007C7C: BF800000
	s_nop 0                                                    // 000000007C80: BF800000
	s_nop 0                                                    // 000000007C84: BF800000
	s_nop 0                                                    // 000000007C88: BF800000
	s_nop 0                                                    // 000000007C8C: BF800000
	s_nop 0                                                    // 000000007C90: BF800000
	s_nop 0                                                    // 000000007C94: BF800000
	s_nop 0                                                    // 000000007C98: BF800000
	s_nop 0                                                    // 000000007C9C: BF800000
	s_nop 0                                                    // 000000007CA0: BF800000
	s_nop 0                                                    // 000000007CA4: BF800000
	s_nop 0                                                    // 000000007CA8: BF800000
	s_nop 0                                                    // 000000007CAC: BF800000
	s_nop 0                                                    // 000000007CB0: BF800000
	s_nop 0                                                    // 000000007CB4: BF800000
	s_nop 0                                                    // 000000007CB8: BF800000
	s_nop 0                                                    // 000000007CBC: BF800000
