# Bullet vehicle controls: native inputs and destinations

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7`; DLL SHA256 prefix `76141df9` [observed].
Target: `<game install>\PZBullet64.dll` [observed].

**[observed]** This inventory covers the 13 JNI entries and their supporting callees, producing
43 parameter rows in [bullet-vehicle-io.csv](../modding/data/bullet-vehicle-io.csv). Argument indices exclude
JNIEnv/jclass. Names `var0` through `var7` are the available Java declaration names, not recovered original source names.
**[observed]** Types match the native boundary survey's JNI descriptors; entry addresses agree with the [export inventory](bullet-native.md).

## Confidence rubric and field notation

- **[observed]** `high` records an argument reaching a concrete field/call with the stated conversion or arithmetic.
  It does not certify a physical unit or prove later simulation outcomes.
- **[inferred]** `medium` records concrete data flow whose higher-level meaning depends on arithmetic interpretation,
  partially understood consumers, or a mixed-purpose array layout; it is not assigned from name similarity alone.
- **[unknown]** `low` records a known write whose ultimate effect remains UNVERIFIED; `[unknown]` would mean no
  reliable destination was recovered. All 43 rows have a destination; 33 are high, 7 medium and 3 low.
- **[observed]** `vehicle` denotes the selected record from the map at world offset `+0xa0`; its body pointer is at
  `vehicle+0x10`, and its wheel-system pointer at `vehicle+0x8`. The world pointer is `DAT_1801d5728`.
  Wheel records are selected by `FUN_18004ef90` with stride `0x240`.
- **[inferred]** Conventional names such as force, torque, inertia, velocity and quaternion describe the observed
  arithmetic and related uses; these are not recovered C++ field names. **[unknown]** Physical units remain UNVERIFIED:
  the CSV does not assume kilograms, metres, newtons, seconds or radians from method names.

## controlVehicle

**[observed]** Entry `0x180009cc0` looks up arg0, then `FUN_1800126b0` routes arg1 to `FUN_18004e960`/wheel `+0x200`, arg2 into `FUN_18004f4a0`/`+0x208`, and arg3 to `FUN_18004f4e0`/`+0x1d8`, subject to per-wheel configuration/flags and a burnt-vehicle guard.
**[inferred]** Arg3 is an orientation/steering input because `FUN_1800510b0` consumes that slot in rotation construction; **[unknown]** its angular units and the final drive/brake interpretation of args1/2 remain UNVERIFIED because downstream wheel dispatch was not resolved.

## setVehicleParams

**[observed]** Entry `0x18000e390` selects arg0 and reads arg1 in six-float groups per wheel: element 0 sets vehicle wheel flag `+0xc9` using a threshold, 1 writes inflation `+0xc4`, 3/4 write wheel `+0x1c8/+0x1c0`, and 5 offsets wheel `+0x1a0` from a script field.
**[observed]** Element 2 temporarily writes wheel `+0x1d0`, but a later branch overwrites that slot in the same iteration; element 0 also selects wheel `+0x1b0/+0x1d0` values. The entry checks array length against six times wheel count; **[unknown]** physical units and the exact semantic names of these tuning fields are unproven.

## setVehicleMass

**[observed]** Entry `0x18000e250` selects arg0, supplies arg1 to a shape virtual call, then calls `FUN_180042810`, which writes reciprocal mass at body `+0x2a0`, inverse local inertia at `+0x310/+0x318/+0x320`, and mass-dependent factors.
**[observed]** Zero selects a collision-flag branch at body `+0x1a0`; **[unknown]** the mass unit and the virtual shape implementation are not established.

## setVehicleStatic

**[observed]** Entry `0x18000e770` passes arg0's record and arg1's boolean to `FUN_180014820`: on a state transition, true selects zero mass and flag `0x2`, while false restores the script mass from the record at vehicle `+0x68`, field `+0x28`.
**[observed]** The transition stores vehicle `+0xc0`, clears body motion/force fields, and invokes world remove/re-add operations through virtual slots; **[unknown]** those dynamic targets were not resolved, and restoring the last value passed to `setVehicleMass` is not what this code shows.

## setVehicleActive

**[observed]** Entry `0x18000e170` passes arg0 and arg1 through `FUN_180031d50` to `FUN_180014740`; it rejects activation when vehicle `+0xc0` is set, otherwise writes vehicle `+0xc1` and calls `FUN_180070540`.
**[observed]** True writes activation-state field body `+0x1ac` as 4, false as 1; **[unknown]** false must not be described as putting the body to sleep without further evidence.

## applyCentralForceToVehicle

**[observed]** Entry `0x180009760` selects the vehicle with arg0; args1/2/3 add to body `+0x330/+0x338/+0x340`, respectively, after multiplying by body `+0x2b0/+0x2b8/+0x2c0`.
**[inferred]** These are central-force accumulator components; **[unknown]** their physical units, Java coordinate convention and subsequent integration timing are unproven.

## applyTorqueToVehicle

**[observed]** Entry `0x180009a50` selects arg0's vehicle; args1/2/3 add to body `+0x350/+0x358/+0x360`, scaled by corresponding fields at `+0x2b0..+0x2c0` and `+0x430..+0x440`.
**[inferred]** This is a torque-accumulation path; **[unknown]** torque units and coordinate convention are not established.

## applyForce

**[observed]** Entry `0x1800098b0` uses arg0 in the separate world map at `+0xb8`; `FUN_18001c970` and `FUN_1800167f0` use arg1 as a body pointer-array index via `FUN_180018270` and read arg2's first six floats as two vectors.
**[observed]** Floats 0..2 reach body force fields `+0x330..+0x340`; floats 3..5 contribute through a cross product to torque fields `+0x350..+0x360`. **[inferred]** The second vector is a relative application offset; **[unknown]** this group key is not established as interchangeable with a vehicle ID.

## applyImpulse

**[observed]** Entry `0x180009980` uses arg0 in world map `+0xb8`, arg1 as the body-array index, and arg2 as six floats; `FUN_18001ca30` reaches `FUN_180016920`, then `FUN_180017990` for the angular part.
**[observed]** For nonzero inverse mass, floats 0..2 immediately modify body `+0x260..+0x270` using that inverse mass; floats 3..5 supply the cross-product offset affecting `+0x280..+0x290`. **[inferred]** These are linear/angular velocity changes rather than the force accumulator writes above; **[unknown]** units remain unproven.

## setVehicleVelocityMultiplier

**[observed]** Entry `0x18000e870` selects arg0 and widens args1/2 into doubles at vehicle `+0x70/+0x78`; `FUN_1800126b0` divides absolute wheel-system speed by the first field and clamps its contribution to the inflation-related control penalty.
**[inferred]** Arg1 therefore acts as a speed normalization scale, rather than an observed direct multiplication of body velocity. **[unknown]** Arg2's consumer and physical effect remain UNVERIFIED; the CSV assigns that row low confidence.

## teleportVehicle

**[observed]** Entry `0x18000f0d0` selects arg0; args1/2 subtract world integer offsets `+0x40/+0x44` and become body transform components `+0x70/+0x80`, while arg3 becomes `+0x78`; args4..7 enter `FUN_180007c40` before transform setter `FUN_180042630`.
**[inferred]** The four-component conversion constructs a quaternion-derived rotation basis. **[observed]** The entry also clears body motion vectors `+0x260..+0x298` and removes/re-adds the body through world virtual calls; **[unknown]** physical distance units and those dynamic targets remain unproven.

## setTireInflation

**[observed]** Entry `0x18000de30` selects arg0 and bounds-checks arg1 against configured wheel count; arg2 is stored as a float at vehicle `+0xc4+8*wheelIndex`.
**[observed]** `FUN_1800126b0` reads that field in a one-minus-input penalty below its threshold, scaled by the speed normalization above; **[unknown]** a pressure unit or a guaranteed gameplay inflation scale is not established.

## setTireRemoved

**[observed]** Entry `0x18000df80` selects arg0, bounds-checks wheel index arg1, and stores boolean arg2 at vehicle `+0xc8+8*wheelIndex`; it selects base/reduced wheel `+0x1b0` and script/fixed wheel `+0x1d0` values.
**[observed]** It then refreshes wheel transforms through `FUN_180051720` and `FUN_1800510b0`. **[unknown]** The separate `setVehicleParams` flag at vehicle `+0xc9` is not this removed flag, and the final handling effect is unproven.

## What a modder can change and what happens

- **[observed]** The mass input changes reciprocal mass/inertia storage; the static toggle restores script mass on returning
  to the non-static state, so it can supersede an earlier mass override.
- **[observed]** Teleport changes a complete pose and clears motion fields. The active toggle writes activation states;
  it is not an evidenced replacement for teleport, mass changes or sleeping.
- **[observed]** Per-wheel inputs select bounded wheel records; the packed parameter array has six entries per wheel,
  with an overwritten temporary input and a flag distinct from the removed flag.
- **[inferred]** The force/impulse paths offer different immediate effects, but reaching them from a mod safely requires
  establishing their caller-side IDs, coordinate conventions and units. **[unknown]** No new Lua-callable route or safe
  gameplay tuning range is established by these native findings.

## Confidence and limits

- **[observed]** The CSV contains 43 rows for 13 natives, sorted by native and numeric argument index.
- **[observed]** `setTireInflation` arg2 writes an indexed float at `0x18000ded8`.
- **[observed]** `setVehicleVelocityMultiplier` arg1 converts float to double and writes at `0x18000e909/0x18000e912`.
- **[observed]** `applyCentralForceToVehicle` arg1 scales, adds and stores at
  `0x180009816/0x180009822/0x18000983a/0x18000984a`.
- **[unknown]** Runtime execution, gameplay outcomes and physical unit calibration remain unproven.
  **[unknown]** Java callers above the declarations, script-to-native paths, network authority and safe input ranges
  remain unestablished. Names and arithmetic suggest some roles; those interpretations are explicitly tagged.
- **[unknown]** Virtual shape/world operations and downstream wheel dispatch remain unresolved. Exception-tail jumps
  and terminal calls do not establish runtime call coverage or absence of later effects.
- **[unknown]** The consumer of vehicle `+0x78` and the final meaning of control slots wheel `+0x200/+0x208` remain
  UNVERIFIED. Array lengths and indices should not be generalized beyond the checks stated for each entry.
