# Bullet ragdolls: native inputs and destinations

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7`; DLL SHA256 prefix `76141df9` [observed].
Target: `<game install>\PZBullet64.dll` [observed].

**[observed]** This inventory covers the 23 entry names and supporting callees, with 68 parameter rows in
[bullet-ragdoll-io.csv](../modding/data/bullet-ragdoll-io.csv). Argument indices exclude JNIEnv/jclass/jobject.
**[observed]** Scope correction against native boundary and export inventories: 22 entries are in `zombie.core.physics.Bullet`;
`renderRagdoll` is in `zombie.core.physics.PhysicsDebugRenderer`, not Bullet. It remains in scope under its actual class.
**[observed]** Types match the native boundary survey's JVM descriptors; available Java names are `var0` onwards for Bullet,
and `var1/var2/var3` for the renderer declaration at `PhysicsDebugRenderer.java:280`. These are not original source names.

## Confidence rubric and field notation

- **[observed]** `high` records an argument reaching a concrete field/call with the stated conversion or arithmetic.
  It does not certify a physical unit or prove later simulation outcomes.
- **[inferred]** `medium` records concrete data flow whose higher-level meaning depends on arithmetic interpretation,
  partially understood consumers, or a mixed-purpose array layout; it is not assigned from name similarity alone.
- **[unknown]** `low` records a known write whose ultimate effect remains UNVERIFIED; `[unknown]` would mean no
  reliable destination was recovered. This table has 49 high, 12 medium and 7 low rows; no unknown rows.
  The seven low rows are add-time transform inputs whose temporary writes and forwarding are known, but final use is not.
- **[observed]** `world` is `DAT_1801d5728`; its instance map is at `+0xb8`, with a reuse pool at `+0xc8..+0xe8`.
  `ragdoll` denotes the map/pool record; `dynamics` is its `+0x28` pointer and `skeleton` its `+0x30` pointer.
  Instance ID is stored at `ragdoll+0xc0`, membership flag at `+0xd0`, and cached mass at `+0xc8`.
- **[observed]** `builder` is the singleton returned by `FUN_1800061b0`; `script` is the object at its first pointer.
  Template arrays are at `script+0x18/+0x30/+0x48/+0x60` for constraints/anchors/body parts/dynamics.
  Offsets are byte offsets, not recovered C++ field declarations.
- **[inferred]** Rotation/basis and motion labels follow conversion/arithmetic and Java caller data.
  **[unknown]** Physical units, axis conventions and safe ranges remain UNVERIFIED; physical inputs use `[unknown]` units.

## Script definitions versus runtime objects

**[observed]** Yes: ragdoll configuration is a game-script object type, `ScriptType.Ragdoll`.
`ScriptModule.java:481–493` constructs `RagdollScript` objects in a script bucket.
The installed `media/scripts/ragdolls/` directory contains `ragdoll_anchors.txt` (34 ragdoll blocks),
`ragdoll_bodydynamics.txt` (11), `ragdoll_bodypartinfo.txt` (11), and `ragdoll_constraints.txt` (10).
These counts are block declarations, not native instances.

**[observed]** `RagdollScript.Load` (`zombie/scripting/objects/RagdollScript.java:111–123`) parses the script block
and dispatches by its identifier suffix. The collection's `PostLoadScripts`
(`zombie/scripting/ScriptManager.java:463–465`) calls `RagdollScript.toBullet(false)`.
That method (`RagdollScript.java:101–108`) uploads all four template families when `GameServer.server` is false.
The four `defineRagdoll*` calls below are therefore post-script-load uploads; their boolean also supports a live-refresh path.

**[observed]** This differs from creating an item/vehicle-style named native instance: the upload arguments are packed arrays
and a boolean; `addRagdoll` takes an instance ID and transform values, with no script-name argument.
Parsed records occupy shared template arrays indexed by joint/bone/body-part identifiers.
**[inferred]** A script block defines part of the shared ragdoll configuration, rather than proving a separately selectable
ragdoll archetype for each named block. **[unknown]** Arbitrary new archetype support and mod override precedence were not established.

| Phase [observed from callers and native flow] | Scoped natives [observed] |
|---|---|
| Script configuration upload (4) | defineRagdollAnchors; defineRagdollBodyDynamics; defineRagdollBodyPartInfo; defineRagdollConstraints |
| Shared builder initialization/tuning (3) | initializeRagdollPose; initializeRagdollSkeleton; setRagdollMass |
| Runtime instance operations (12) | addRagdoll; removeRagdoll; getRagdollSimulationState; resetRagdollBodyDynamics; setRagdollActive; setRagdollBodyDynamics; setRagdollLocalTransformRotation; simulateRagdoll; simulateRagdollWithRigidBodyOutput; updateRagdoll; updateRagdollSkeletonPreviousTransforms; updateRagdollSkeletonTransforms |
| Debug controls/rendering (4) | drawDebugRagdollBodyParts; drawDebugRagdollSkeleton; highlightRagdollBodyPart; PhysicsDebugRenderer.renderRagdoll |

**[observed]** The native boundary survey caller distinction is confirmed: uploads are at `RagdollScript.java:342,362,377,395`;
runtime add/remove calls are at `RagdollController.java:223,232`. Builder initialization is at
`zombie/characters/RagdollBuilder.java:65,101`, and its mass setter calls the native at line 154.
**[unknown]** The table describes phases evidenced by these paths, not exclusive runtime call coverage.

## addRagdoll

**[observed]** Entry `0x180008f10` passes arg0 through `FUN_18002d9f0` for instance-map insertion, allocating
or reusing a record; arg1/arg3 subtract world offsets `+0x40/+0x44`, arg2 remains the middle placement component,
and args4..7 pass through `FUN_180007c40` to build a temporary rotation basis.
**[unknown]** The transform is forwarded through the fresh-allocation constructor chain to `FUN_180017bd0`,
where no transform-argument read was recovered; the reuse branch instead calls `FUN_18001dbe0` to reset the record.
Placement/rotation effects from these seven inputs remain UNVERIFIED, so those rows are low.
**[observed]** The recovered `FUN_18001c8b0` tail only logs; it does not itself demonstrate world membership insertion.

## defineRagdollAnchors

**[observed]** Entry `0x180009f90` sends arg0 to `FUN_18001b630`, which reads five-float tuples and stores
12-byte anchor records through `script+0x30`; the Java uploader identifies bone, body part and three flags.
Arg1 gates `FUN_18001e950 -> thunk_FUN_180018560` refreshes of current and pooled ragdolls.
**[unknown]** Accepted index ranges and final anchor effects are not fully established.

## defineRagdollBodyDynamics

**[observed]** Entry `0x18000a200` sends arg0 to `FUN_18001b7c0`, filling 32-byte records through `script+0x60`
from eight-float tuples; Java labels part, two damping inputs, deactivation, two sleeping thresholds and two friction inputs.
Arg1 gates shared `FUN_180007f50`, which rebuilds builder shapes and refreshes existing objects.
**[unknown]** That refresh is not proof that every dynamics value immediately changes every existing body.

## defineRagdollBodyPartInfo

**[observed]** Entry `0x18000a360` sends arg0 to `FUN_18001b970`, filling 64-byte records through `script+0x48`
from ten-float tuples: part, calculate-length flag, radius/height/gap, shape, mass and three offset components.
Arg1 gates `FUN_180007f50 -> FUN_180038a20/FUN_18001e9a0`; the shared refresh also visits existing ballistics targets.
**[unknown]** Shape units, allowed enum values and resulting collision behaviour remain unproven.

## defineRagdollConstraints

**[observed]** Entry `0x18000a4c0` sends arg0 to `FUN_18001bb80`, filling `0xd0`-byte records through
`script+0x18` from 22-float tuples: four selectors and six three-component groups.
Arg1 gates `FUN_18001e9b0 -> FUN_18001a100` rebuilds for current and pooled ragdolls.
**[observed]** Java upload order identifies the groups as two axes, two offsets, limits and extended limits.
**[unknown]** Angle units and accepted constraint-type values are not established.

## drawDebugRagdollBodyParts

**[observed]** Entry `0x18000ab50` uses arg0 to select the instance and stores boolean args1/2 at
`ragdoll+0x14/+0x11`; Java caller labels them body drawing and single-part drawing.
**[unknown]** The final renderer interpretation remains unproven.

## drawDebugRagdollSkeleton

**[observed]** Entry `0x18000ac70` selects arg0 and stores boolean args1/2 at `ragdoll+0x12/+0x13`;
Java caller labels them skeleton drawing and single-part drawing.
**[unknown]** These flags do not establish a simulation change.

## getRagdollSimulationState

**[observed]** Entry `0x18000b8d0` selects arg0 and calls `FUN_18001d240`, which compares activation fields
`body+0x1ac` across eleven bodies, returning a shared state or zero on disagreement; missing ID returns -1.
**[unknown]** Numeric activation-state meanings and runtime transition timing were not calibrated.

## highlightRagdollBodyPart

**[observed]** Entry `0x18000bf60` selects arg0 and stores arg1 at `ragdoll+0x24`.
**[unknown]** The downstream highlight consumer and allowed selector values remain UNVERIFIED.

## initializeRagdollPose

**[observed]** Entry `0x18000c1a0` forwards to `FUN_180037c10`: arg0 is a bone count, arg1 supplies
seven floats per bone (three position components and four rotation components), and args2..5 construct builder/root rotation
through `FUN_180007c40`. It composes parent transforms and refreshes builder body-part shapes.
**[observed]** The root transform is replaced by the supplied root rotation; this is shared builder initialization,
not an ID-addressed instance pose setter.

## initializeRagdollSkeleton

**[observed]** Entry `0x18000c250` forwards arg0 as a bone count and arg1 as parent indices to `FUN_1800383a0`,
which resizes and fills the hierarchy vector at `builder+0x90`.
**[unknown]** Arbitrary hierarchy topology, negative counts and mismatched input lengths are not established as safe.

## removeRagdoll

**[observed]** Entry `0x18000c5b0` forwards arg0 to `FUN_1800312c0`, which removes the instance-map entry
and transfers its record to the reuse pool.
**[observed]** Its `FUN_18001dbc0` hook has an empty recovered body; removal is not demonstrated to free the record
or remove all dynamic bodies by itself.

## renderRagdoll

**[observed]** `PhysicsDebugRenderer.renderRagdoll`, entry `0x180040650`, checks native/debug-renderer context,
selects arg0's ragdoll and invokes `FUN_18001dbd0 -> FUN_18001cd20`; args1/2 become doubles at
`world+0x80/+0x90`. The Java caller supplies `ddwX/ddwY` at `PhysicsDebugRenderer.java:98`.
**[unknown]** This is debug-render context, not an evidenced gameplay pose or simulation setter.

## resetRagdollBodyDynamics

**[observed]** Entry `0x18000c6d0` matches arg0 against record field `+0xc0` in current/pool searches, then calls
`FUN_18001dcc0 -> FUN_180018df0`, passing eleven selected bodies through the shared-table helper `FUN_180036d00`.
**[inferred]** This is a configured-dynamics reset path; **[unknown]** exact restored field values and restoration of unrelated pose/mass state were not independently re-derived inside that final helper.

## setRagdollActive

**[observed]** Entry `0x18000da80` selects arg0 and passes boolean arg1 to `FUN_18001dd70`;
on a transition it writes `ragdoll+0xd0` and uses `FUN_180015d50/FUN_180018cf0` for body/constraint
world add/remove calls. Both paths reset body motion vectors.
**[unknown]** World virtual dispatch targets and externally visible timing remain unproven.

## setRagdollBodyDynamics

**[observed]** Entry `0x18000dae0` uses arg0 to select the matching instance and arg1 in `FUN_18001c170`.
That parser repeatedly writes the same eight-field temporary, rather than indexing an output array;
the retained record then reaches `FUN_180007de0 -> FUN_18001e970 -> FUN_1800197d0`.
**[observed]** The final helper loops eleven bodies, supplying damping to `FUN_180042770` and storing
deactivation/sleeping/friction inputs at `body+0x1b0/+0x3a8/+0x1b8/+0x1c8`.
**[inferred]** With a complete multi-tuple input, the recovered path applies the last retained tuple across those bodies;
per-tuple body-specific overrides must not be assumed. **[unknown]** Partial-input outcomes are unproven.

## setRagdollLocalTransformRotation

**[observed]** Entry `0x18000dc70` selects arg0; args1..4 reach `FUN_18001ddd0 -> FUN_180007c40`,
which writes a local basis at `ragdoll+0x40..+0x98` and clears its translation slots.
**[unknown]** Units and a guaranteed immediate change of rigid-body world poses are not established.

## setRagdollMass

**[observed]** Entry `0x18000dce0` writes arg0 as a double at `builder+0xf8`, then calls `FUN_18001dea0`
for all current and pooled ragdolls; it caches the value at `ragdoll+0xc8` and passes the same value to
`FUN_180042810` for each of eleven bodies, using shape-derived inertia data.
**[unknown]** This is not established as a total mass divided among parts, and no physical mass unit is certified.

## simulateRagdoll

**[observed]** Entry `0x18000e980` selects arg0, pins output arg1 and calls `FUN_18001dff0`, which synchronizes
body/skeleton data and writes seven floats per bone through `FUN_18001c760`, returning the bone count.
**[unknown]** The established path does not establish that this entry advances a physics timestep; units and world-space
interpretation of every returned transform remain unproven.

## simulateRagdollWithRigidBodyOutput

**[observed]** Entry `0x18000ec90` selects arg0 and sends output args1/2 to `FUN_18001df50`:
arg1 gets the skeleton output above; arg2 gets eleven seven-float body transforms from `FUN_180018280`.
A later `FUN_180017a70` call bounds body motion-vector magnitude; it does not use arg2 as another output.
**[unknown]** The JNI entry only checks both arrays are nonempty, not that they have sufficient complete-output capacity.

## updateRagdoll

**[observed]** Entry `0x18000fb10` selects arg0 and forwards to `FUN_18001e890`: args1/2/3 write placement
at `ragdoll+0xe0/+0xe8/+0xf0` and `dynamics+0x70/+0x78/+0x80`, with world offsets subtracted from args1/3;
args4..7 construct the dynamics rotation basis at `+0x10`.
**[unknown]** This storage behaviour does not guarantee an immediate teleport of every rigid body.

## updateRagdollSkeletonPreviousTransforms

**[observed]** Entry `0x18000fca0` selects arg0; `FUN_18001e9c0` passes bone count arg1 and packed
seven-float records arg3 through `FUN_18001d2b0`, then supplies arg2 to `FUN_180016a70`.
**[observed]** The latter uses the reciprocal of arg2 in body-motion calculations.
**[inferred]** It is an interval scale, consistent with the Java caller's `deltaT`; **[unknown]** its time unit and zero handling are unproven.

## updateRagdollSkeletonTransforms

**[observed]** Entry `0x18000fe20` selects arg0 and forwards bone count arg1 and packed transform arg2 to
`FUN_18001ec80 -> FUN_18001d2b0`; seven floats per bone become hierarchical transforms, then
`FUN_1800354a0/FUN_180019180` update skeleton/body transform data.
**[unknown]** Compatibility of arbitrary skeleton lengths and bone orders is not established.

## What a modder can change and what happens

- **[observed]** The four installed ragdoll script families feed shared native arrays through four post-load definition
  uploads. Joint/anchor/body-part/dynamics inputs have concrete parsing destinations; live refresh is a separate boolean path.
  **[unknown]** This does not establish arbitrary new named ragdoll archetypes or safe script ranges.
- **[observed]** Runtime instance IDs address separate records; builder bone counts are not instance IDs.
  Active transitions change world membership, while update calls write placement/basis data and skeleton paths synchronize transforms.
- **[observed]** The mass setter is global across the builder and current/pool records, applying one value per body.
  **[inferred]** Treating it as a per-character total-mass control would misrepresent the established path.
- **[observed]** Dynamics overrides reach damping and body fields; resets reach a shared-table helper for eleven bodies.
  **[unknown]** The recovered tuple-overwrite path prevents promising independent overrides for every input tuple.
- **[unknown]** Add-time transform effect, direct Lua/mod routes, safe lifecycle/authority, physical units and runtime
  gameplay outcomes remain unproven. Pose-output methods are not interchangeable with an evidenced physics-step API.

## Confidence and limits

- **[observed]** The inventory covers 23 entries and 68 argument tokens matching the JVM descriptors.
- **[observed]** `highlightRagdollBodyPart` arg1 stores an integer at `0x18000bfad`.
- **[observed]** `drawDebugRagdollSkeleton` arg1 stores a boolean at `0x18000ad26`.
- **[observed]** `PhysicsDebugRenderer.renderRagdoll` arg1 converts integer to double and stores at
  `0x1800406cb/0x1800406cf/0x1800406e1`.
- **[observed]** Script-type registration, post-load uploads and runtime add/remove are distinct paths in the Java
  locations cited above; the installed ragdoll block counts cover all four game script files.
- **[observed]** Rows sort by qualified native then numeric argument index; the CSV has eight columns.
  The reset-row effect is limited to the identified helper.
- **[unknown]** Runtime execution, gameplay effects and unit calibration remain unestablished.
  **[unknown]** Complete Java call-chain/mod routes, network authority and safe tuning ranges remain unproven.
  Static branches and stores do not establish actual invocation.
- **[unknown]** Virtual shape/world targets and final debug rendering effects remain incompletely resolved.
  The add-time transform is computed/forwarded but has no recovered final consumer in the creation chain.
- **[observed]** Definition wrappers do not propagate the template parser's returned success status; they return success
  after the array-access/upload path. **[unknown]** A true JNI result therefore does not certify schema validity or complete application.
  Array dimensions, template indices, hierarchy order and pointer lifetime require caller-side validation.
- **[unknown]** The packed-array and retained-tuple conclusions describe static data flow; malformed/partial arrays
  and exception-tail behaviour remain unproven. Input/output buffer minimum capacity is not proven by a nonempty check.
