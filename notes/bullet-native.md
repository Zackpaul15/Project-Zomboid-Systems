# PZBullet64 native export inventory

Survey date: 2026-10-25. Game build: Project Zomboid Build 42, `projectzomboid.jar` sha256 prefix `e1a69eb7` [observed in R0].
Target: `F:\SteamLibrary\steamapps\common\ProjectZomboid\PZBullet64.dll`, 2,061,824 bytes [observed].
DLL SHA256: `76141df900f08ef71c0808bcd6248c929c47b8c5900b86af4875131a780897ef` [observed].

## Boundary

**[observed]** This x86-64 Windows shared library exports the Java physics entry points catalogued in
[R0](native-boundary.md). R0 records `Bullet` loading `PZBullet64` and attributes five `PhysicsDebugRenderer`
natives to the same DLL by inference. The export table now provides a name match for every one of those declarations.
**[inferred]** The entry-point names identify a physics bridge covering vehicles, ragdolls, ballistics and world updates;
the names alone do not establish their implementation behaviour.

## Export totals and join

- **[observed]** The PE export directory has 103 address-table slots and 103 named exports, with no unnamed live slots,
  zero targets or forwarded exports. All 103 target addresses correspond to Ghidra-recognized functions.
- **[observed]** 98 names start with `Java_`; the other 5 are C++-decorated function exports beginning with `?Java_`.
  The CSV classifies those 5 as `is_jni=no` under the requested literal-prefix rule, with `java_native=[none]` and
  `dll_confidence=[n/a]`. Their runtime use is **[unknown]**; a JNI-like substring does not establish Java binding.
- **[observed]** R0 assigns 98 declarations to this DLL: 93 in `zombie.core.physics.Bullet` and 5 in
  `zombie.core.physics.PhysicsDebugRenderer`. All 98 resolve to distinct exported names; unresolved declarations: **none**.
  No `Java_*` export is left unmatched by this join.
- **[observed]** The CSV preserves R0's confidence values: 93 `direct`, 5 `inferred`. The five inferred assignments
  now have export-name evidence, but this deliverable copies R0 rather than revising its confidence column.
- **[observed]** Expected names were formed by escaping literal `_` as `_1` before replacing class-name dots with `_`.
  `PhysicsDebugRenderer.n_debugDrawWorld` matches `Java_zombie_core_physics_PhysicsDebugRenderer_n_1debugDrawWorld`.
  None of the 98 declarations shares a class/method name with an overload, so no long-name descriptor suffix was needed.

## Resolved JNI exports by feature area

**[inferred]** Areas below classify names, not verified behaviour. Each of the 98 matched JNI exports is counted once;
debug-renderer methods take precedence, followed by ballistics, ragdoll/skeleton, constraints, vehicles, meshes,
rigid objects/transforms, and the remaining world/streaming/bridge methods. **[observed]** Counts total 98.

| Feature area [inferred] | Exports [observed] |
|---|---:|
| Ragdoll and skeleton | 25 |
| Ballistics and aiming | 21 |
| Vehicles | 20 |
| World, streaming and bridge | 13 |
| Constraints | 7 |
| Rigid objects and transforms | 5 |
| Debug rendering | 5 |
| Mesh and shape definitions | 2 |
| **Total** | **98** |

## What a modder can act on

**[observed]** Java declarations for vehicle control and mass, tire state, constraints, forces/impulses,
ragdoll simulation, ballistics targeting, physics meshes, world stepping and debug rendering have concrete
exported function entry points in this installed DLL. Examples include `setVehicleMass`, `setConstraintERP`,
`applyImpulse`, `simulateRagdoll`, `updateBallistics`, `definePhysicsMesh` and `stepSimulation`.
**[inferred]** These are useful Java-wrapper starting points for R2 tracing; the join establishes entry-point presence,
not that every routine performs the operation suggested by its name. **[observed]** R0 records no direct Lua binding
for these natives. **[unknown]** Mod-accessible wrapper routes and safe parameter changes were not established here.

## Verification and regeneration

- **[observed]** One DLL session and one Ghidra 12.1.4 default auto-analysis pass completed. Export data was read through
  REA's Ghidra `read_bytes` at image base `0x180000000`: directory RVA `0x1cd760`, length 6,796 bytes.
  Directory Evidence: `ev_616fb45dad171b37de9b3f8c29dc4656fc5adf6692c1777ab321a00721a8f217`.
- **[observed]** An independent source-file read located the same export directory at file offset `0x1cc160` by parsing
  the PE section headers. Its directory matched Ghidra's read completely; independent enumeration again gave 103 exports.
  Ghidra procedure inventory Evidence: `ev_d8c4196825c0c768dca573bbe61afc1c46e823227d7f922a6ba5599075b89521`.
- **[observed]** Three randomly selected names were checked against the source-file export table and separately through
  Ghidra `list_names` at their exported addresses: `Java_zombie_core_physics_Bullet_updateBallisticsAimReticleRotation`
  (`0x18000f680`), `Java_zombie_core_physics_Bullet_setBallisticsTargetAxis` (`0x18000cb00`), and
  `Java_zombie_core_physics_Bullet_setBallisticsTargetAllPartsColor` (`0x18000cac0`). All matched exactly.
- **[observed]** CSV file generation iteration count: **2**. The first used Ghidra's export-directory enumeration;
  after deleting the CSV, the second used the independently enumerated source-file exports. Both files had SHA256
  `bf63370a73647c8155d9e886372456e5393cb40d79830afcd50735fdbd6cdad8`, confirming byte-identical regeneration.
  Regeneration sorts exact export names in
  ordinal string order, joins expected JNI names to R0, copies R0 confidence, and writes the requested six columns with LF
  line endings. Fixed notes distinguish matched JNI exports from unmatched decorated exports.
  No generator script was added outside this task's two owned repository paths.
- **[observed]** Retained Evidence and snapshot were saved under
  `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\` as `r1-bullet-evidence.json` and
  `r1-bullet-snapshot.json`; `close_binary` completed. **[unknown]** The REA-managed ephemeral Ghidra project/log location
  was not exposed by these tool calls, so placement of those internal intermediates under the requested scratch root is UNVERIFIED.

## Limits

- **[observed]** This pass inventories exported names and their function addresses; it does not decompile function bodies
  or execute the DLL. The five C++-decorated names retain their exact export-table spelling in the CSV.
- **[unknown]** Behaviour, argument meaning, units, valid ranges, side effects, and the effect of changing a script value
  are not established by this pass; those require R2 evidence.
- **[unknown]** Nested calls, indirect calls, runtime registration, and whether a matched entry point is ever invoked
  are unproven. Export presence does not prove a useful implementation or a reachable mod API.
