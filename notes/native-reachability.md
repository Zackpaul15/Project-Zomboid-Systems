# Native reachability from Lua: source join

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7` [observed in R0].

**[observed]** [native-reachability.csv](../modding/data/native-reachability.csv) contains all 392 R0 rows in the
same order. The first five fields are copied unchanged, and R0's representative caller class is preserved.
This pass uses source/text analysis and exposure tables only; no DLL was opened and Ghidra was not started.

## Counts and scope

- **[observed]** The join records **51 yes** and **341 [unknown]** Lua routes; it never emits `no`.
  Among the 33 R2a/R2b natives, **21** have a route and **12** remain unknown.
- **[observed]** R0's 355 known representative caller classes remain known; its 37 unknown callers remain unknown.
  Calling-method visibility was located for 354 rows: 288 public, 4 protected, 44 private and 18 package.
  The remaining 38 are the 37 unknown callers plus `ClipperOffset.newInstance`, invoked by a field initializer.
- **[inferred]** **59** native rows have only private/package callers **among the located lexical sites**.
  These are bounded search results, not proof that no public Java caller exists elsewhere.
  **[unknown]** A global count of natives called exclusively from private/package Java is UNVERIFIED.
  In particular, a private immediate caller can have an exposed ancestor method.
- **[observed]** Route confidence is high for 37 rows, medium for 14, and unknown for 341.
  The broad source survey examined 3,093 `src/zombie/**/*.java` files; bundled libraries and runtime reflection were not surveyed.

**[observed]** Per-DLL counts below describe the generated join. **[inferred]** The last column counts rows with
only private/package sites in the bounded lexical candidate inventory, not a whole-program access guarantee.

| R0 DLL value | Total [observed] | Lua yes [observed] | Lua unknown [observed] | Only private/package candidates [inferred] |
|---|---:|---:|---:|---:|
| `PZPopMan64.dll` | 59 | 0 | 59 | 2 |
| `PZBullet64.dll` | 98 | 31 | 67 | 16 |
| `ZNetJNI64.dll\|ZNetNoSteam64.dll` | 140 | 7 | 133 | 20 |
| `bink64.dll\|bink2w64.dll` | 11 | 10 | 1 | 0 |
| `Lighting64.dll` | 50 | 3 | 47 | 14 |
| `[unknown]` | 2 | 0 | 2 | 0 |
| `PZPathFind64.dll` | 13 | 0 | 13 | 1 |
| `PZClipper64.dll` | 19 | 0 | 19 | 6 |
| **Total** | **392** | **51** | **341** | **59** |

## Reachability rubric

- **[observed]** A `yes` starts at a public method actually listed for its whitelisted class in
  `exposed-methods.csv`/`exposed-classes.csv`, or at an actual `@LuaMethod(global = true)` on
  `LuaManager.GlobalObject`. A source call sequence must lead from that entry to the native.
  [Binding rules](../modding/lua-api/how-binding-works.md) distinguish registration from ordinary public Java access.
- **[observed]** A public method on an unlisted class is not itself a Lua entry. For example, returning
  `BallisticsController` from `IsoGameCharacter.getBallisticsController` does not register the controller's methods.
  The accepted route uses the exposed `IsoGameCharacter.updateBallistics` implementation instead.
- **[observed]** High confidence means the exposed/annotated entry and direct wrapper link are established in source;
  explicit wrapper-overload links are included where needed. Medium means an identified multi-method,
  conditional source chain; it establishes a potential route, not that a particular invocation takes it.
- **[unknown]** Low would describe a candidate with an unresolved edge and would not be sufficient for `yes`.
  No low-confidence route was promoted. `[unknown]` with `route=[none]` means no eligible route was established,
  including routes rejected as debug-only; it does not assert inaccessibility.
- **[observed]** Debug/reflection-only routes are excluded. This includes the population debug-renderer candidates
  and the `Core.debug` branches that call `setBallisticsSize`/`setBallisticsColor`.
  The direct quaternion initialization has a separate ordinary source path.
- **[observed]** The `java_caller` column retains R0's class/file-level representative, which need not be the caller
  on the chosen route. Visibility describes a located method in that representative file; if several qualify,
  public precedes protected, private, then package. Constructor access was checked separately.
  `LuaManager.GlobalObject` is written explicitly in routes even though R0 records its outer source file.
- **[observed]** `reachable_from_lua` answers a different question from R0's `lua_exposed`, which records only whether
  the native is itself bound/listed. R0 is `no` for all 392 and R3 is `yes` for 51; the two do not conflict — no
  `yes` row reaches the native by binding its own class, each goes through a public wrapper or a `GlobalObject` global.
- **[inferred]** Caller discovery uses qualified native-name hits, same-class wrapper calls, and a second pass for
  representative instance-call files. Method ownership is derived from declaration/indent boundaries, with targeted
  source reads for accepted chains. It is a lexical join, not a complete Java call graph or overload resolver.

## End-to-end chains for the 33 traced natives

**[observed]** Every R2a/R2b native has a row below, including those without a supported mod entry.
Short class names expand to `zombie.vehicles.BaseVehicle`, `zombie.characters.IsoGameCharacter`, and
the named `zombie.core.physics.*` classes. Java steps are identifiers, not copied bodies.
**[inferred]** Effect summaries retain the static-analysis limits of their linked R2 notes; unknown native units
or consumers are not resolved merely by finding a Lua ancestor.

| Lua/mod entry [observed or unknown] | Java caller/chain [observed or unknown] | Native [observed] | Effect summary [R2 evidence and limits] |
|---|---|---|---|
| BaseVehicle.updatePhysics | CarController.update | `Bullet.controlVehicle` | Routes inputs into conditional wheel control/orientation fields. [R2a](bullet-vehicle.md#controlvehicle) |
| BaseVehicle.updateBulletStats | BaseVehicle.updateBulletStats | `Bullet.setVehicleParams` | Reads six floats per wheel; one temporary input is overwritten. [R2a](bullet-vehicle.md#setvehicleparams) |
| BaseVehicle.update | BaseVehicle.update | `Bullet.setVehicleMass` | Writes reciprocal mass and local inverse inertia. [R2a](bullet-vehicle.md#setvehiclemass) |
| BaseVehicle.setPhysicsActive | Bullet.setVehicleStatic(BaseVehicle,boolean) | `Bullet.setVehicleStatic` | Switches zero/script mass and flags; clears motion on transitions. [R2a](bullet-vehicle.md#setvehiclestatic) |
| BaseVehicle.setPhysicsActive | Bullet.setVehicleActive(BaseVehicle,boolean) | `Bullet.setVehicleActive` | Writes active state and activation field; activation is rejected while static. [R2a](bullet-vehicle.md#setvehicleactive) |
| BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | `Bullet.applyCentralForceToVehicle` | Adds scaled components to the body force accumulator. [R2a](bullet-vehicle.md#applycentralforcetovehicle) |
| BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | `Bullet.applyTorqueToVehicle` | Adds scaled components to the body torque accumulator. [R2a](bullet-vehicle.md#applytorquetovehicle) |
| [none] [unknown] | RagdollController.simulateHitReaction | `Bullet.applyImpulse` | Changes selected body linear/angular velocity using a six-float input. [R2a](bullet-vehicle.md#applyimpulse) |
| [none] [unknown] | [unknown] | `Bullet.applyForce` | Accumulates force and cross-product torque on a selected body. [R2a](bullet-vehicle.md#applyforce) |
| BaseVehicle.update | BaseVehicle.updateVelocityMultiplier | `Bullet.setVehicleVelocityMultiplier` | Writes two fields; first is a speed-normalization divisor. [R2a](bullet-vehicle.md#setvehiclevelocitymultiplier) |
| BaseVehicle.setWorldTransform | BaseVehicle.setWorldTransform | `Bullet.teleportVehicle` | Sets pose with offset/component conversion and clears motion. [R2a](bullet-vehicle.md#teleportvehicle) |
| BaseVehicle.setTireInflation | BaseVehicle.setTireInflation | `Bullet.setTireInflation` | Writes the indexed inflation field used by control penalties. [R2a](bullet-vehicle.md#settireinflation) |
| BaseVehicle.setTireRemoved | BaseVehicle.setTireRemoved | `Bullet.setTireRemoved` | Changes the removed flag and wheel tuning, then refreshes transforms. [R2a](bullet-vehicle.md#settireremoved) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update -> BallisticsTarget.addToWorld | `Bullet.addBallisticsTarget` | Finds/creates a target and requests collision-object registration. [R2b](bullet-ballistics.md#addballisticstarget) |
| [none] [unknown] | BallisticsController.getCameraTargets | `Bullet.getBallisticsCameraTargets` | Writes five-float results, optionally with body-part annotations. [R2b](bullet-ballistics.md#getballisticscameratargets) |
| [none] [unknown] | BallisticsController.getTargets | `Bullet.getBallisticsTargets` | Uses an explicit ray extent and writes four-float hit records. [R2b](bullet-ballistics.md#getballisticstargets) |
| [none] [unknown] | BallisticsController.getSpreadData | `Bullet.getBallisticsTargetsSpreadData` | Samples lateral offsets and writes four floats per sample. [R2b](bullet-ballistics.md#getballisticstargetsspreaddata) |
| IsoGameCharacter.releaseBallisticsController | BallisticsController.releaseController -> BallisticsController.removeFromWorld | `Bullet.removeBallistics` | Queues the controller for reuse and removes its map entry. [R2b](bullet-ballistics.md#removeballistics) |
| IsoGameCharacter.releaseBallisticsTarget | BallisticsTarget.releaseTarget -> BallisticsTarget.removeFromWorld | `Bullet.removeBallisticsTarget` | Requests collision removal and queues/removes the target. [R2b](bullet-ballistics.md#removeballisticstarget) |
| [none] [unknown] | BallisticsController.update | `Bullet.setBallisticsColor` | Writes the controller colour vector copied into hit metadata. [R2b](bullet-ballistics.md#setballisticscolor) |
| [none] [unknown] | BallisticsController.setRange | `Bullet.setBallisticsRange` | Writes stored sample range used by update processing. [R2b](bullet-ballistics.md#setballisticsrange) |
| [none] [unknown] | BallisticsController.update | `Bullet.setBallisticsSize` | Sends a uniform three-component vector to two virtual calls. [R2b](bullet-ballistics.md#setballisticssize) |
| [none] [unknown] | RagdollBuilder.Initialize | `Bullet.setBallisticsTargetAdjustingShapeScale` | Writes three global components; final shape effect is unverified. [R2b](bullet-ballistics.md#setballisticstargetadjustingshapescale) |
| [none] [unknown] | PhysicsDebugRenderer.init | `Bullet.setBallisticsTargetAllPartsColor` | Writes a shared vector supplied to per-part rendering calls. [R2b](bullet-ballistics.md#setballisticstargetallpartscolor) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update | `Bullet.setBallisticsTargetAxis` | Builds and stores a target rotation basis. [R2b](bullet-ballistics.md#setballisticstargetaxis) |
| IsoGameCharacter.updateBallistics | BallisticsController.update | `Bullet.updateBallistics` | Updates controller/sample positions when stored range is positive. [R2b](bullet-ballistics.md#updateballistics) |
| IsoGameCharacter.updateBallistics | BallisticsController.update | `Bullet.updateBallisticsAimReticlePosition` | Writes reticle position with two world-offset subtractions. [R2b](bullet-ballistics.md#updateballisticsaimreticleposition) |
| IsoGameCharacter.updateBallistics | BallisticsController.update -> BallisticsController.initialize | `Bullet.updateBallisticsAimReticleQuaternion` | Replaces reticle/sample matrices and a shared orientation basis. [R2b](bullet-ballistics.md#updateballisticsaimreticlequaternion) |
| [none] [unknown] | [unknown] | `Bullet.updateBallisticsAimReticleRotate` | Composes reticle orientation; sample bases use supplied rotation. [R2b](bullet-ballistics.md#updateballisticsaimreticlerotate) |
| [none] [unknown] | [unknown] | `Bullet.updateBallisticsAimReticleRotation` | Builds reticle/sample bases through normalized axis-angle arithmetic. [R2b](bullet-ballistics.md#updateballisticsaimreticlerotation) |
| IsoGameCharacter.updateBallistics | BallisticsController.update | `Bullet.updateBallisticsMuzzleAimDirection` | Builds controller/sample orientation from direction components. [R2b](bullet-ballistics.md#updateballisticsmuzzleaimdirection) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update | `Bullet.updateBallisticsTarget` | Updates target position; five trailing forwarded arguments lack recovered reads. [R2b](bullet-ballistics.md#updateballisticstarget) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update -> BallisticsTarget.updateSkeleton | `Bullet.updateBallisticsTargetSkeleton` | Builds hierarchical transforms from seven floats per node. [R2b](bullet-ballistics.md#updateballisticstargetskeleton) |

**[observed]** Activation/static routes include `Bullet.setVehicleActive(BaseVehicle,boolean)` and
`Bullet.setVehicleStatic(BaseVehicle,boolean)`, which call the integer-ID natives; matching the name alone
would omit a real wrapper step. `BaseVehicle.updateVelocityMultiplier` and several target/controller helpers
are private, but their accepted ancestor routes begin at exposed methods.
**[unknown]** The query/range methods on the unlisted `BallisticsController` have ordinary Java callers in
`CombatManager`; no full exposed ancestor chain was established here. No route is inferred just from their public access.

## Verification and reproducibility

- **[observed]** Three R0 unknown callers were investigated with a case-sensitive call-token search over the source
  survey. `Bullet.applyForce` appears only at its declaration (`Bullet.java:491`);
  `Bullet.isWorldInit` only at its declaration (`Bullet.java:95`);
  `VideoTexture.getFrameDataSize` only at its private declaration (`VideoTexture.java:187`).
  **[unknown]** None can be assigned a concrete caller from those results; reflection/undecompiled paths remain unverified.
  Zero of R0's 37 unknown callers was promoted without evidence.
- **[observed]** Three yes rows were re-derived by a second source read and checked against the exposure table:
  `BaseVehicle.setTireInflation` at lines 8525-8526 calls the native directly;
  `VideoTexture.Close` at lines 92-94 calls `closeVideo`;
  `IsoGameCharacter.updateBallistics` at lines 16138-16145 calls `BallisticsController.update`,
  whose line 98 calls `Bullet.updateBallistics`. Each root is listed in `exposed-methods.csv`.
- **[observed]** Additional overload/source checks covered `Bullet.java:302-309` (activation/static wrappers),
  `BaseVehicle.java:3578-3592` (private velocity update), `IsoGameCharacter.java:8683-8685` and
  `:8822` (update ancestry), and `BallisticsTarget.java:80-110,172-174,185-214` (target update/release ancestry).
- **[observed]** Global entries were checked directly in `LuaManager.java`: `inviteFriend` (7706-7712),
  `getCurrentUserProfileName` (7760-7762), `activateSteamOverlayToWebPage` (7796-7800),
  `configureLighting` (8390-8393), and `addPhysicsObject` (9098-9100).
  Each carries the actual global annotation, rather than being accepted merely because it is public.
- **[observed]** CSV generation iteration count: **2**. The second generation re-read R0 and repeated the join from
  the same evidence/route mapping after deleting the first CSV; both outputs were byte-identical. CSV SHA256:
  `b5ade5a1b3c880cab25fab5541f301fdff3d3a568715ad320947c02da80ac92b`.
  All 392 ordered first-five-field tuples
  and all representative caller classes remained identical to R0. No generator file was added outside the two owned paths.

## Limits

- **[unknown]** Lua exposure does not establish usable mod execution: object availability, sandbox restrictions,
  lifecycle, client/server authority, timing and branch preconditions remain unresolved. This is an invocation path,
  not a recommendation to call lifecycle/update methods manually or a claim of direct native argument control.
- **[unknown]** Reflection/debug reachability is not counted. Debug-only alternatives may exist even where this join
  reports `[none]`; exclusion is not an absence claim.
- **[unknown]** The `java_caller` link is a text match and can miss aliases, lambdas, callbacks, method references,
  indirect calls or the correct overload. Instance-call coverage outside representative files is incomplete;
  the 59 private/package-only candidates therefore cannot establish global exclusivity.
- **[unknown]** Search candidates and manually supported routes are not an exhaustive transitive closure.
  Several public Java wrappers and ordinary engine chains remain untraced; all unresolved rows stay unknown.
  Native behaviour, physical units and safe script-value changes retain the R2a/R2b limitations.
