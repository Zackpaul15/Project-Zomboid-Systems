# PZBullet64 native export inventory

Survey date: 2026-10-25. Game build: Project Zomboid Build 42, `projectzomboid.jar` sha256 prefix `e1a69eb7` [observed].
Target: `<game install>\PZBullet64.dll`, 2,061,824 bytes [observed].
DLL SHA256: `76141df900f08ef71c0808bcd6248c929c47b8c5900b86af4875131a780897ef` [observed].

## Boundary

**[observed]** This x86-64 Windows shared library exports the Java physics entry points catalogued in
[native boundary survey](native-boundary.md). The native boundary survey records `Bullet` loading `PZBullet64` and attributes five `PhysicsDebugRenderer`
natives to the same DLL by inference. The export table now provides a name match for every one of those declarations.
**[inferred]** The entry-point names identify a physics bridge covering vehicles, ragdolls, ballistics and world updates;
the names alone do not establish their implementation behaviour.

## Export totals and join

- **[observed]** The PE export directory has 103 address-table slots and 103 named exports, with no unnamed live slots,
  zero targets or forwarded exports. All 103 target addresses correspond to recognized functions.
- **[observed]** 98 names start with `Java_`; the other 5 are C++-decorated function exports beginning with `?Java_`.
  The CSV classifies those 5 as `is_jni=no` under the literal-prefix rule, with `java_native=[none]` and
  `dll_confidence=[n/a]`. Their runtime use is **[unknown]**; a JNI-like substring does not establish Java binding.
- **[observed]** The native boundary survey assigns 98 declarations to this DLL: 93 in `zombie.core.physics.Bullet` and 5 in
  `zombie.core.physics.PhysicsDebugRenderer`. All 98 resolve to distinct exported names; unresolved declarations: **none**.
  No `Java_*` export is left unmatched by this join.
- **[observed]** The CSV preserves the native boundary survey's confidence values: 93 `direct`, 5 `inferred`. The five inferred assignments
  now have export-name evidence, and the CSV retains the native boundary survey's confidence column.
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
**[inferred]** These Java wrappers have matching native entry points; this establishes entry-point presence,
not that every routine performs the operation suggested by its name. **[observed]** The native boundary survey records no direct Lua binding
for these natives. **[unknown]** Mod-accessible wrapper routes and safe parameter changes were not established here.

## Confidence and limits

- **[observed]** The PE export directory has image base `0x180000000`, RVA `0x1cd760` and length 6,796 bytes.
- **[observed]** Its file offset is `0x1cc160`; the file and loaded directory agree on all 103 exports.
- **[observed]** `Java_zombie_core_physics_Bullet_updateBallisticsAimReticleRotation` is at `0x18000f680`.
- **[observed]** `Java_zombie_core_physics_Bullet_setBallisticsTargetAxis` is at `0x18000cb00`.
- **[observed]** `Java_zombie_core_physics_Bullet_setBallisticsTargetAllPartsColor` is at `0x18000cac0`.
- **[observed]** The CSV has six columns, exact export names in ordinal string order, and the native boundary survey's
  confidence values. Matched JNI exports and unmatched decorated exports have distinct notes.
- **[observed]** The five C++-decorated names retain their exact export-table spelling in the CSV.
- **[unknown]** This inventory establishes exported names and function addresses; function-body behaviour and runtime
  execution remain unproven.
- **[unknown]** Argument meanings, units, valid ranges, side effects and script-value effects require implementation evidence.
- **[unknown]** Nested calls, indirect calls, runtime registration and actual invocation remain unproven.
  Export presence does not prove a useful implementation or a reachable mod API.
