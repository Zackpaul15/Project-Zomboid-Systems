# Bullet ballistics and aiming: native inputs and destinations

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7`; DLL SHA256 prefix `76141df9` [observed, R0/R1].
Target: `F:\SteamLibrary\steamapps\common\ProjectZomboid\PZBullet64.dll` [observed].

**[observed]** This static pass covers the 20 requested JNI entries and supporting callees, producing 76 parameter rows
in [bullet-ballistics-io.csv](../modding/data/bullet-ballistics-io.csv). Argument indices exclude JNIEnv/jclass.
Names `var0` through `var8` are the available decompiled Java declaration names, not recovered original source names.
**[observed]** Types come from R0's descriptors; entry identities agree with the [R1 inventory](bullet-native.md).

## Scope reconciliation

**[observed]** Both counts in the brief describe different scopes: the R1 feature group contains **21** methods,
whereas this requested slice contains **20**. The additional R0/R1 row is `zombie.core.physics.Bullet.getTargetedBodyPart`,
resolved by `Java_zombie_core_physics_Bullet_getTargetedBodyPart`; it is deliberately not traced or included in this CSV.
**[inferred]** R1's feature grouping is a name-based classification, not a declaration of this pass's scope.

## Confidence rubric and field notation

- **[observed]** `high` records a traced argument reaching a concrete field/call with the stated conversion or arithmetic.
  It does not certify a physical unit or prove later simulation outcomes.
- **[inferred]** `medium` records concrete data flow whose higher-level meaning depends on arithmetic interpretation,
  partially understood consumers, or a mixed-purpose array layout; it is not assigned from name similarity alone.
- **[unknown]** `low` records a known write whose ultimate effect remains UNVERIFIED; `[unknown]` would mean no
  reliable destination was recovered. Forwarding writes to a callee's outgoing argument area count as a known write,
  not as proof of consumption. **[observed]** The 76 rows comprise 45 high, 22 medium and 9 low.
- **[observed]** The world pointer is `DAT_1801d5728`; controller keys use world map `+0xf0`, while target keys use
  world map `+0x128`. `controller` and `target` below name the selected records, not shared field layouts.
- **[inferred]** Quaternion, axis, direction, colour and spread labels describe arithmetic or observed consumers,
  not recovered C++ field names. **[unknown]** Physical distance/angle/colour scales are UNVERIFIED; `[unknown]` is used
  rather than assuming metres, radians, degrees or normalized RGB. `quaternion component` denotes a mathematical role.

## addBallisticsTarget

**[observed]** Entry `0x180008870` uses arg0 as a target key, creates/reuses a record through `FUN_180007390` if missing, and reaches `FUN_1800236a0`, which checks membership before requesting addition of target `+0x68` through the world virtual slot `+0x40`.
**[unknown]** The dynamic world target and its full runtime effects are unresolved; this is registration evidence, not a demonstrated projectile hit.

## removeBallistics

**[observed]** Entry `0x18000c330` passes arg0 to `FUN_180030c10`, which selects the controller, enqueues it in the reuse structure at world `+0x100`, and erases its map entry at world `+0xf0`.
**[unknown]** This pass does not establish when pooled storage is reused or all later effects of removal.

## removeBallisticsTarget

**[observed]** Entry `0x18000c390` selects target arg0, invokes `FUN_1800260f0` for conditional world removal via virtual `+0x48`, enqueues the record at world `+0x138`, and erases its target-map entry.
**[unknown]** The world dispatch target remains unresolved; queueing is not evidence that the target object is immediately destroyed.

## getBallisticsCameraTargets

**[observed]** Entry `0x18000adf0` maps arg0 to `FUN_18001fef0`; arg1 filters first-pass hits by distance from controller position, arg2 limits emitted targets, arg3 enables temporary body registration plus a second ray pass, and arg4 receives five-float records.
**[observed]** Records initially contain an identifier, three offset-restored hit coordinates and marker 11; `FUN_180023290` can replace the fifth element with a selected body-part index. The ray endpoints are built around reticle position/basis with a fixed native scale; arg1 is a filter, not that construction scale.

## getBallisticsTargets

**[observed]** Entry `0x18000af70` selects controller arg0; `FUN_180020a50` uses arg1 to form the forward endpoint, arg2 to stop after emitted hits, and arg3 for four-float records containing identifier plus three offset-restored hit coordinates.
**[observed]** It reaches the collision query `FUN_180021d20` and updates recognized hits' metadata; the count comparison occurs after a record write. **[unknown]** No complete buffer-capacity guarantee follows from the JNI wrapper's nonempty-array check.

## getBallisticsTargetsSpreadData

**[observed]** Entry `0x18000b0e0` selects arg0's controller and calls `FUN_180020580`: arg1 supplies forward extent, arg2 scales random lateral radius, arg3 enters the power-like radius transform `FUN_180144170`, arg4 controls sample iterations, and arg6 receives four floats per sample.
**[observed]** Each record starts as zero ID plus endpoint coordinates and can become recognized-hit data; arg5 is forwarded but has no recovered consumer in the helper. **[inferred]** Arg3 shapes the radial distribution; **[unknown]** its gameplay scale and arg5's effect remain UNVERIFIED.

## setBallisticsColor

**[observed]** Entry `0x18000c930` selects controller arg0 and passes widened args1/2/3 to `FUN_180022790`, writing controller `+0xc0/+0xc8/+0xd0`; ordinary hit-query processing copies this vector to recognized-hit metadata.
**[unknown]** Colour encoding/range, renderer behaviour and any gameplay consequence are not established.

## setBallisticsRange

**[observed]** Entry `0x18000c9c0` selects controller arg0; arg1 reaches `FUN_1800227b0` and double field controller `+0xa0`, which `FUN_180022860` uses for its positive-range guard, sample spacing and endpoint construction.
**[unknown]** This does not establish a weapon maximum range: `getBallisticsTargets` separately uses its own explicit extent argument, and physical distance units are unproven.

## setBallisticsSize

**[observed]** Entry `0x18000ca20` selects controller arg0; `FUN_1800227c0` repeats arg1 into a three-component vector passed through virtual `+0x28` on objects stored at controller `+0x98` and `+0x1a0`.
**[inferred]** This is consistent with uniform shape scaling; **[unknown]** those virtual implementations, valid sizes and resulting collision dimensions are unresolved.

## setBallisticsTargetAdjustingShapeScale

**[observed]** Entry `0x18000ca80` widens args0/1/2 directly into globals `DAT_1801d56e0/DAT_1801d56e8/DAT_1801d56f0`; it does not select a target ID.
**[unknown]** Bounded cross-reference checks on these addresses exposed initialization/setter writes but no established shape consumer; their final effect remains UNVERIFIED, so all three rows are low confidence.

## setBallisticsTargetAllPartsColor

**[observed]** Entry `0x18000cac0` widens args0/1/2 into `DAT_1801d56c0/DAT_1801d56c8/DAT_1801d56d0`; `FUN_180025d10` passes the shared vector to renderer virtual `+0x30` while enumerating target bodies.
**[unknown]** Exact channel encoding and rendered appearance are unproven; no damage modification is established by this global vector write.

## setBallisticsTargetAxis

**[observed]** Entry `0x18000cb00` selects target arg0; `FUN_1800261f0` uses args1/2/3 in separate half-angle constructions, composes a four-component orientation, and reaches `FUN_180007c40` before storing target basis `+0x90..+0xe8`.
**[inferred]** These are composed rotation inputs; **[unknown]** physical angular units and caller coordinate conventions remain UNVERIFIED.

## updateBallistics

**[observed]** Entry `0x18000f3a0` finds/creates controller arg0 through `FUN_18002d270`, subtracts world offsets `+0x40/+0x44` from args1/3, and passes those plus unchanged arg2 to `FUN_180022860`.
**[observed]** That helper writes controller position `+0x60/+0x68/+0x70` and sample translations only when stored range `+0xa0` is positive; **[unknown]** coordinate units and later runtime scheduling are not established.

## updateBallisticsAimReticlePosition

**[observed]** Entry `0x18000f490` selects controller arg0, subtracts world `+0x40` from arg1 and world `+0x44` from arg3, leaves arg2 unshifted, and reaches `FUN_180022be0`, storing reticle position at controller `+0x180/+0x188/+0x190`.
**[unknown]** The physical distance scale is unproven; these components are not reordered like R2a's Java vehicle-teleport position inputs.

## updateBallisticsAimReticleQuaternion

**[observed]** Entry `0x18000f540` selects controller arg0; args1..4 enter `FUN_180022c00`, which uses `FUN_180007c40` to replace controller reticle basis `+0x120`, the sample bases, and shared basis `DAT_1801d5630`.
**[inferred]** The arithmetic is a four-component quaternion-to-matrix conversion; **[unknown]** caller conventions and safe degenerate inputs remain UNVERIFIED.

## updateBallisticsAimReticleRotate

**[observed]** Entry `0x18000f5e0` selects controller arg0; `FUN_180022c90` converts the current reticle basis through `FUN_1800078a0`, composes it with args1..4, and writes the composed basis via `FUN_180007c40`.
**[observed]** Sample bases are rebuilt from the supplied four components rather than that composed local result; **[inferred]** this distinguishes relative reticle composition from absolute sample replacement, without establishing gameplay intent.

## updateBallisticsAimReticleRotation

**[observed]** Entry `0x18000f680` selects controller arg0; args1..3 supply a normalized axis and arg4 supplies half-angle terms before `FUN_180022e70` replaces the reticle/sample bases through `FUN_180007c40`.
**[inferred]** This is an axis-angle construction, distinct from the direct four-component methods; **[unknown]** angular units, axis conventions and valid zero-axis behaviour are not established.

## updateBallisticsMuzzleAimDirection

**[observed]** Entry `0x18000f7f0` selects controller arg0; `FUN_180022ef0` combines args1/2/3 with reference-vector globals in cross-product and normalization operations, then replaces controller basis `+0x0..+0x58` and the ordinary sample bases via `FUN_180007c40`.
**[inferred]** These are direction components used to construct orientation, rather than directly assigned world positions; **[unknown]** required input normalization and coordinate conventions remain unproven.

## updateBallisticsTarget

**[observed]** Entry `0x18000f850` finds/creates target arg0, subtracts world offsets from args1/3, and reaches `FUN_1800264f0`, which writes args1/2/3 to target `+0x70/+0x78/+0x80`, copies position into an associated record, and requests collision-representation refresh.
**[observed]** Instruction listings show args4..8 forwarded on the outgoing stack, but no reads of those incoming slots in `FUN_1800264f0`; **[unknown]** their effective meaning remains UNVERIFIED. All five are retained as low-confidence rows, rather than inventing orientation or flag effects from the Java declaration.

## updateBallisticsTargetSkeleton

**[observed]** Entry `0x18000f9f0` finds/creates target arg0 and supplies arg1's node count plus arg2's float array to `FUN_180026590`, which reads seven floats per node as three translation components and four orientation components.
**[observed]** It replaces the first generated transform with the target basis/transform, composes later nodes through a parent-index table, then reaches `FUN_1800354a0` and `FUN_180019180`; **[unknown]** original bone naming, units and complete caller-side validation are unproven.

## What a modder can change and what happens

- **[observed]** Controller position, reticle position and target position are separate destinations; setters use
  distinct controller/target keys. Two world-offset subtractions occur on position paths, without proving units.
- **[observed]** The direct quaternion, relative quaternion composition and normalized-axis construction use different
  paths. Updating the direct quaternion also writes a shared basis; it is not solely a private controller-field update.
- **[observed]** Query extent, stored sample range, random lateral scale, distribution-shaping input and sample count
  reach different calculations. Camera queries can perform temporary body registration and annotate body-part results.
- **[unknown]** No weapon damage effect, safe tuning range, Lua-callable route or complete script-to-native path is
  established. The scale globals, unused helper option and trailing target-update arguments need further evidence.

## Verification and reproducibility

- **[observed]** REA/Ghidra 12.1.4 returned all 20 requested entries successfully. Entry batch Evidence:
  `ev_eff22520926ef8ca3d8ce1760ecd3a660e2ce8854bc6ad3810c25c24a4a1e810`.
  Setter/helper batch: `ev_f813dc8f81006c9c4ceb0908043824e09f5296ac0ddc9ec09d49957f5318d24d`;
  getter batch: `ev_7481a3c442aeb8f04a36d764b6a492cd922ebb57db8395d436552f1d7bdfa5aa`.
- **[observed]** Three parameter rows were independently re-derived from instruction listings after decompilation:
  `setBallisticsRange` arg1's widening/store at `0x1800227b3/0x1800227b7`;
  `setBallisticsTargetAdjustingShapeScale` arg0's widening/global store at `0x18000ca86/0x18000ca8e`;
  and `updateBallisticsAimReticlePosition` arg2's widened input at `0x18000f4ea/0x18000f501`, followed by
  its packed-vector destination at `0x180022be7` (controller `+0x188`).
  All three routes agreed. No listings were copied into this repository.
- **[observed]** Instruction-level argument tracing also corrected Ghidra's incomplete recovered signatures:
  target-update forwarding appears at `0x18000f967..0x18000f9c5`, while spread arg3 enters floating register XMM1
  at `0x18002068a` before the random-radius transform call at `0x18002068e`.
- **[observed]** CSV generation iteration count: **2**, including deletion and regeneration before the second output.
  Both files were byte-identical; rows are sorted by native and numeric argument index, with types checked against
  R0 and names taken from the available Java declarations. CSV SHA256:
  `4eb72542f59a81e674ffb8fb04828d490a78b112a66f498f8b8828bd2c563cee`.
  No generator file was added outside the two owned repository paths.
- **[observed]** Retained Evidence and snapshot use the requested scratch directory under
  `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\`, as `r2b-ballistics-evidence.json` and
  `r2b-ballistics-snapshot.json`; `close_binary` completed.

## Limits

- **[unknown]** No runtime execution, Java caller-stack trace, weapon/script integration, calibrated physical units,
  network authority or safe gameplay value range was established.
- **[unknown]** Collision-world, shape and renderer virtual dispatch targets remain unresolved. Ghidra reports some
  exception-tail jumps and terminal-call boundaries; recovered pseudocode signatures are not authoritative JNI types.
- **[observed]** The three query JNI wrappers check only that output-array length is at least one. Helpers write
  four floats per ordinary hit/spread sample or five per camera result; this pass does not establish caller buffer capacity.
  **[unknown]** Full bounds safety and all special/degenerate-input behaviour remain unproven.
- **[unknown]** No recovered consumer establishes the final shape-scale effect, spread arg5's effect, or effects of
  target-update args4..8. Bounded cross-reference results are not proof that a value is unused everywhere.
- **[unknown]** REA exposes no caller-selected internal Ghidra project/log directory through these tools; placement of
  ephemeral internal intermediates under the scratch root remains UNVERIFIED. Explicit retained artifacts use scratch.
