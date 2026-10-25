# Native reachability from Lua: source join

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7` [observed].

**[observed]** [native-reachability.csv](../modding/data/native-reachability.csv) contains all 392 native boundary survey rows in the
same order. The first five fields are copied unchanged, and the native boundary survey's representative caller class is preserved.
This table establishes Java/Lua source-level routes and exposure, without establishing native implementation behaviour.

## Counts and scope

- **[observed]** The join records **51 yes** and **341 [unknown]** Lua routes; it never emits `no`.
  Among the 33 vehicle/ballistics natives, **21** have a route and **12** remain unknown.
- **[observed]** The native boundary survey's 355 known representative caller classes remain known; its 37 unknown callers remain unknown.
  Calling-method visibility was located for 354 rows: 288 public, 4 protected, 44 private and 18 package.
  The remaining 38 are the 37 unknown callers plus `ClipperOffset.newInstance`, invoked by a field initializer.
- **[inferred]** **59** native rows have only private/package callers **among the located lexical sites**.
  These are bounded search results, not proof that no public Java caller exists elsewhere.
  **[unknown]** A global count of natives called exclusively from private/package Java is UNVERIFIED.
  In particular, a private immediate caller can have an exposed ancestor method.
- **[observed]** Route confidence is high for 37 rows, medium for 14, and unknown for 341.
  Source coverage includes 3,093 `zombie/**/*.java` files; bundled libraries and runtime reflection are outside its scope.

**[observed]** Per-DLL counts below describe the reachability table. **[inferred]** The last column counts rows with
only private/package sites in the bounded lexical candidate inventory, not a whole-program access guarantee.

| native boundary survey DLL value | Total [observed] | Lua yes [observed] | Lua unknown [observed] | Only private/package candidates [inferred] |
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
- **[observed]** The `java_caller` column retains the native boundary survey's class/file-level representative, which need not be the caller
  on the chosen route. Visibility describes a located method in that representative file; if several qualify,
  public precedes protected, private, then package. Constructor access is distinct from method visibility.
  `LuaManager.GlobalObject` is written explicitly in routes even though the native boundary survey records its outer source file.
- **[observed]** `reachable_from_lua` answers a different question from the native boundary survey's `lua_exposed`, which records only whether
  the native is itself bound/listed. The native boundary survey is `no` for all 392 and the Lua reachability survey is `yes` for 51; the two do not conflict — no
  `yes` row reaches the native by binding its own class, each goes through a public wrapper or a `GlobalObject` global.
- **[inferred]** Caller candidates reflect qualified native names, same-class wrappers and instance calls in
  representative files. Method ownership depends on declaration/indent boundaries. These textual associations
  do not constitute a complete Java call graph or overload resolution.

## End-to-end chains for the 33 vehicle/ballistics natives

**[observed]** Every vehicle/ballistics native has a row below, including those without a supported mod entry.
Short class names expand to `zombie.vehicles.BaseVehicle`, `zombie.characters.IsoGameCharacter`, and
the named `zombie.core.physics.*` classes. Java steps are identifiers, not copied bodies.
**[inferred]** Effect summaries retain the static-analysis limits of their linked native input notes; unknown native units
or consumers are not resolved merely by finding a Lua ancestor.

| Lua/mod entry [observed or unknown] | Java caller/chain [observed or unknown] | Native [observed] | Effect summary [native input evidence and limits] |
|---|---|---|---|
| BaseVehicle.updatePhysics | CarController.update | `Bullet.controlVehicle` | Routes inputs into conditional wheel control/orientation fields. [vehicle inputs](bullet-vehicle.md#controlvehicle) |
| BaseVehicle.updateBulletStats | BaseVehicle.updateBulletStats | `Bullet.setVehicleParams` | Reads six floats per wheel; one temporary input is overwritten. [vehicle inputs](bullet-vehicle.md#setvehicleparams) |
| BaseVehicle.update | BaseVehicle.update | `Bullet.setVehicleMass` | Writes reciprocal mass and local inverse inertia. [vehicle inputs](bullet-vehicle.md#setvehiclemass) |
| BaseVehicle.setPhysicsActive | Bullet.setVehicleStatic(BaseVehicle,boolean) | `Bullet.setVehicleStatic` | Switches zero/script mass and flags; clears motion on transitions. [vehicle inputs](bullet-vehicle.md#setvehiclestatic) |
| BaseVehicle.setPhysicsActive | Bullet.setVehicleActive(BaseVehicle,boolean) | `Bullet.setVehicleActive` | Writes active state and activation field; activation is rejected while static. [vehicle inputs](bullet-vehicle.md#setvehicleactive) |
| BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | `Bullet.applyCentralForceToVehicle` | Adds scaled components to the body force accumulator. [vehicle inputs](bullet-vehicle.md#applycentralforcetovehicle) |
| BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | BaseVehicle.applyAccumulatedImpulsesFromHitObjectsToPhysics | `Bullet.applyTorqueToVehicle` | Adds scaled components to the body torque accumulator. [vehicle inputs](bullet-vehicle.md#applytorquetovehicle) |
| [none] [unknown] | RagdollController.simulateHitReaction | `Bullet.applyImpulse` | Changes selected body linear/angular velocity using a six-float input. [vehicle inputs](bullet-vehicle.md#applyimpulse) |
| [none] [unknown] | [unknown] | `Bullet.applyForce` | Accumulates force and cross-product torque on a selected body. [vehicle inputs](bullet-vehicle.md#applyforce) |
| BaseVehicle.update | BaseVehicle.updateVelocityMultiplier | `Bullet.setVehicleVelocityMultiplier` | Writes two fields; first is a speed-normalization divisor. [vehicle inputs](bullet-vehicle.md#setvehiclevelocitymultiplier) |
| BaseVehicle.setWorldTransform | BaseVehicle.setWorldTransform | `Bullet.teleportVehicle` | Sets pose with offset/component conversion and clears motion. [vehicle inputs](bullet-vehicle.md#teleportvehicle) |
| BaseVehicle.setTireInflation | BaseVehicle.setTireInflation | `Bullet.setTireInflation` | Writes the indexed inflation field used by control penalties. [vehicle inputs](bullet-vehicle.md#settireinflation) |
| BaseVehicle.setTireRemoved | BaseVehicle.setTireRemoved | `Bullet.setTireRemoved` | Changes the removed flag and wheel tuning, then refreshes transforms. [vehicle inputs](bullet-vehicle.md#settireremoved) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update -> BallisticsTarget.addToWorld | `Bullet.addBallisticsTarget` | Finds/creates a target and requests collision-object registration. [ballistics inputs](bullet-ballistics.md#addballisticstarget) |
| [none] [unknown] | BallisticsController.getCameraTargets | `Bullet.getBallisticsCameraTargets` | Writes five-float results, optionally with body-part annotations. [ballistics inputs](bullet-ballistics.md#getballisticscameratargets) |
| [none] [unknown] | BallisticsController.getTargets | `Bullet.getBallisticsTargets` | Uses an explicit ray extent and writes four-float hit records. [ballistics inputs](bullet-ballistics.md#getballisticstargets) |
| [none] [unknown] | BallisticsController.getSpreadData | `Bullet.getBallisticsTargetsSpreadData` | Samples lateral offsets and writes four floats per sample. [ballistics inputs](bullet-ballistics.md#getballisticstargetsspreaddata) |
| IsoGameCharacter.releaseBallisticsController | BallisticsController.releaseController -> BallisticsController.removeFromWorld | `Bullet.removeBallistics` | Queues the controller for reuse and removes its map entry. [ballistics inputs](bullet-ballistics.md#removeballistics) |
| IsoGameCharacter.releaseBallisticsTarget | BallisticsTarget.releaseTarget -> BallisticsTarget.removeFromWorld | `Bullet.removeBallisticsTarget` | Requests collision removal and queues/removes the target. [ballistics inputs](bullet-ballistics.md#removeballisticstarget) |
| [none] [unknown] | BallisticsController.update | `Bullet.setBallisticsColor` | Writes the controller colour vector copied into hit metadata. [ballistics inputs](bullet-ballistics.md#setballisticscolor) |
| [none] [unknown] | BallisticsController.setRange | `Bullet.setBallisticsRange` | Writes stored sample range used by update processing. [ballistics inputs](bullet-ballistics.md#setballisticsrange) |
| [none] [unknown] | BallisticsController.update | `Bullet.setBallisticsSize` | Sends a uniform three-component vector to two virtual calls. [ballistics inputs](bullet-ballistics.md#setballisticssize) |
| [none] [unknown] | RagdollBuilder.Initialize | `Bullet.setBallisticsTargetAdjustingShapeScale` | Writes three global components; final shape effect is unverified. [ballistics inputs](bullet-ballistics.md#setballisticstargetadjustingshapescale) |
| [none] [unknown] | PhysicsDebugRenderer.init | `Bullet.setBallisticsTargetAllPartsColor` | Writes a shared vector supplied to per-part rendering calls. [ballistics inputs](bullet-ballistics.md#setballisticstargetallpartscolor) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update | `Bullet.setBallisticsTargetAxis` | Builds and stores a target rotation basis. [ballistics inputs](bullet-ballistics.md#setballisticstargetaxis) |
| IsoGameCharacter.updateBallistics | BallisticsController.update | `Bullet.updateBallistics` | Updates controller/sample positions when stored range is positive. [ballistics inputs](bullet-ballistics.md#updateballistics) |
| IsoGameCharacter.updateBallistics | BallisticsController.update | `Bullet.updateBallisticsAimReticlePosition` | Writes reticle position with two world-offset subtractions. [ballistics inputs](bullet-ballistics.md#updateballisticsaimreticleposition) |
| IsoGameCharacter.updateBallistics | BallisticsController.update -> BallisticsController.initialize | `Bullet.updateBallisticsAimReticleQuaternion` | Replaces reticle/sample matrices and a shared orientation basis. [ballistics inputs](bullet-ballistics.md#updateballisticsaimreticlequaternion) |
| [none] [unknown] | [unknown] | `Bullet.updateBallisticsAimReticleRotate` | Composes reticle orientation; sample bases use supplied rotation. [ballistics inputs](bullet-ballistics.md#updateballisticsaimreticlerotate) |
| [none] [unknown] | [unknown] | `Bullet.updateBallisticsAimReticleRotation` | Builds reticle/sample bases through normalized axis-angle arithmetic. [ballistics inputs](bullet-ballistics.md#updateballisticsaimreticlerotation) |
| IsoGameCharacter.updateBallistics | BallisticsController.update | `Bullet.updateBallisticsMuzzleAimDirection` | Builds controller/sample orientation from direction components. [ballistics inputs](bullet-ballistics.md#updateballisticsmuzzleaimdirection) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update | `Bullet.updateBallisticsTarget` | Updates target position; five trailing forwarded arguments lack recovered reads. [ballistics inputs](bullet-ballistics.md#updateballisticstarget) |
| IsoGameCharacter.update | IsoGameCharacter.updateInternal -> IsoGameCharacter.updateBallisticsTarget -> BallisticsTarget.update -> BallisticsTarget.updateSkeleton | `Bullet.updateBallisticsTargetSkeleton` | Builds hierarchical transforms from seven floats per node. [ballistics inputs](bullet-ballistics.md#updateballisticstargetskeleton) |

**[observed]** Activation/static routes include `Bullet.setVehicleActive(BaseVehicle,boolean)` and
`Bullet.setVehicleStatic(BaseVehicle,boolean)`, which call the integer-ID natives; matching the name alone
would omit a real wrapper step. `BaseVehicle.updateVelocityMultiplier` and several target/controller helpers
are private, but their accepted ancestor routes begin at exposed methods.
**[unknown]** The query/range methods on the unlisted `BallisticsController` have ordinary Java callers in
`CombatManager`; no full exposed ancestor chain was established here. No route is inferred just from their public access.

## Confidence and limits

- **[observed]** `Bullet.applyForce` appears only at its declaration (`Bullet.java:491`);
  `Bullet.isWorldInit` only at its declaration (`Bullet.java:95`);
  `VideoTexture.getFrameDataSize` only at its private declaration (`VideoTexture.java:187`) in the surveyed source.
  **[unknown]** None has an established concrete caller; reflection and unavailable-source paths remain unverified.
  All 37 unknown callers in the native boundary survey remain unknown.
- **[observed]** `BaseVehicle.setTireInflation` at lines 8525-8526 calls the native directly;
  `VideoTexture.Close` at lines 92-94 calls `closeVideo`;
  `IsoGameCharacter.updateBallistics` at lines 16138-16145 calls `BallisticsController.update`,
  whose line 98 calls `Bullet.updateBallistics`. Each root is listed in `exposed-methods.csv`.
- **[observed]** Activation/static wrappers are at `Bullet.java:302-309`; the private velocity update is at
  `BaseVehicle.java:3578-3592`; update ancestry is at `IsoGameCharacter.java:8683-8685` and `:8822`;
  target update/release ancestry is at `BallisticsTarget.java:80-110,172-174,185-214`.
- **[observed]** Global entries in `LuaManager.java` are `inviteFriend` (7706-7712),
  `getCurrentUserProfileName` (7760-7762), `activateSteamOverlayToWebPage` (7796-7800),
  `configureLighting` (8390-8393) and `addPhysicsObject` (9098-9100).
  Each carries the actual global annotation; public visibility alone is insufficient.
- **[observed]** All 392 ordered first-five-field tuples and all representative caller classes match the native boundary survey.
- **[unknown]** Lua exposure does not establish usable mod execution: object availability, sandbox restrictions,
  lifecycle, client/server authority, timing and branch preconditions remain unresolved. This is an invocation path,
  not a recommendation to call lifecycle/update methods manually or a claim of direct native argument control.
- **[unknown]** Reflection/debug reachability is not counted. Debug-only alternatives may exist even where this table
  reports `[none]`; exclusion is not an absence claim.
- **[unknown]** The `java_caller` link is a text match and can miss aliases, lambdas, callbacks, method references,
  indirect calls or the correct overload. Instance-call coverage outside representative files is incomplete;
  the 59 private/package-only candidates therefore cannot establish global exclusivity.
- **[unknown]** Candidate and supported routes are not an exhaustive transitive closure.
  Several public Java wrappers and ordinary engine chains remain unresolved; all unresolved rows stay unknown.
  Native behaviour, physical units and safe script-value changes retain the vehicle/ballistics limitations.
