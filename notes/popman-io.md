# Population spawn/config natives: inputs and destinations

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7` [observed, R0].
Target: install-root `PZPopMan64.dll`, 1,303,040 bytes; SHA256 `5b2e3ef5d383c5e5e6fecf49afd514b196617925c1a0e3623bf0e7917a010ec6` [observed, REA/R7].

**[observed]** This static slice covers exactly nine population-manager natives and 43 parameters in
[popman-io.csv](../modding/data/popman-io.csv). Indices exclude JNIEnv/jclass.
JNI descriptors were independently obtained using `javap -p -s` on the installed jar, then compared with R0;
R0 was used as a cross-check, not as the source of table types.
**[observed]** Available declaration names are `var0` onwards in
`zombie/popman/ZombiePopulationManager.java:92–132`; these are decompiler names, not original source names.
Export identities agree with [R7](popman-native.md).

## Confidence rubric and field notation

- **[observed]** `high` means an argument is traced to a concrete store, map key or consumer call with the stated
  conversion/branch. It does not certify units, a safe range or final gameplay effects.
- **[inferred]** `medium` means concrete flow is recovered, but the row summarizes a mixed-purpose packed array or
  partially interpreted consumer. It is never assigned merely from a method name.
- **[unknown]** `low` would mean a known write with unverified ultimate use; `[unknown]` means no reliable reader or
  destination was recovered. There are 40 high and three medium rows, with no low/unknown rows.
- **[observed]** `work` is the object selected through `*(PTR_DAT_18012f058+0x90)`: pending float/int config maps
  at `+0x40/+0x50`, dirty byte `+0x60`, chunk queue pointer/count `+0x80/+0x7c`,
  zombie queues at `+0x88/+0x98`, real-update pointer/count `+0xc0/+0xbc`, horde pointer/count `+0xd0/+0xcc`.
  These staging offsets are distinct from fields in the receiving population object.
- **[observed]** `population` denotes the receiver of `FUN_18001e9e0`; origin rectangles use the global receiver
  `DAT_180292fd0`. `zombieRecord` is the queued per-zombie data record, not a Java object.
  Other record names denote elements of the corresponding packed arrays; offsets are bytes, not recovered C++ declarations.
- **[unknown]** Physical/time units remain uncalibrated, including settings whose names contain Hours/Day/Distance.
  Those rows retain `units=[unknown]`; identifier, count, key, index, bitfield and boolean-like labels describe verified roles.

## n_config

**[observed]** Entry `0x180026f10` writes nine fixed keys into the pending typed maps and sets `work+0x60`.
Static string construction and the consumer's comparisons identify the keys below; `FUN_18001e9e0` later copies values
to the receiving population fields.

| Arg [observed] | JNI type [observed] | Pending key [observed] | Population destination [observed] |
|---:|---|---|---|
| 0 | F | PopulationMultiplier | +0x168 |
| 1 | F | PopulationStartMultiplier | +0x16c |
| 2 | F | PopulationPeakMultiplier | +0x170 |
| 3 | I | PopulationPeakDay | +0x174 |
| 4 | F | RespawnHours | +0x17c |
| 5 | F | RespawnUnseenHours | +0x178 |
| 6 | F | RespawnMultiplier | +0x180 |
| 7 | F | RedistributeHours | +0xb8 |
| 8 | I | FollowSoundDistance | +0x184 |

**[observed]** R0's `java_caller=[unknown]` is consistent with this bounded check: searching the provided Java tree
for the exact `n_config(` token found only its declaration, and a fresh `javap -c -p` check found no invocation of
`n_config` in its declaring class. Native incoming references inspected here were export/metadata addresses,
not recovered code callers.
**[unknown]** This is not proof that the export is never invoked. Reflection, JNI lookup or another external caller
could reach it; an actual runtime invocation route is UNVERIFIED.

**[observed]** The relationship to named configuration is shared storage, not a demonstrated initial-bulk/later-override
sequence: all nine entries overlap named setters and use the same dirty byte. Java `init(IsoMetaGrid)` calls
`onConfigReloaded`, which calls named setters (`ZombiePopulationManager.java:289–332`).
**[inferred]** Repeated writes to a key replace its pending value; **[unknown]** no current direct Java route for the bulk
entry, or universal cross-thread ordering guarantee, was established.

## n_configFloat

**[observed]** Entry `0x180027040` converts String arg0 through `FUN_180013d20`, validates it using comparisons
in `FUN_180025f00`, stores float arg1 in `work+0x40[key]` through `FUN_180026640`, and marks `work+0x60`.
The recovered key set comprises PopulationMultiplier, PopulationStartMultiplier, PopulationPeakMultiplier,
RespawnHours, RespawnUnseenHours, RespawnMultiplier, RedistributeHours, MinZombiesPerChunk,
MaxZombiesPerChunk and UniformZombiesPerChunk; unmatched keys select an exception path.

**[observed]** Beyond the bulk destinations above, `FUN_18001e9e0` sends MinZombiesPerChunk/MaxZombiesPerChunk/
UniformZombiesPerChunk to `population+0x188/+0x18c/+0x190`.
**[unknown]** The density curve, clamping and numerical gameplay impact after those stores were not established.

## n_configInt

**[observed]** Entry `0x180027290` converts/validates arg0 against PopulationPeakDay and FollowSoundDistance,
writes int arg1 through `FUN_180026510` to `work+0x50[key]`, then sets the same dirty byte.
The receiving config consumer writes `population+0x174/+0x184`.
**[unknown]** There is no established physical unit or valid value range from these map stores alone.

## n_spawnHorde

**[observed]** Entry `0x1800288f0` appends one `0x1c`-byte record: args0..3 are integer rectangle x/y/width/height
at offsets `+0x0/+0x4/+0x8/+0xc`; float target args4/5 occupy `+0x10/+0x14`; count arg6 occupies `+0x18`.
These are pending records, not immediate creation of Java zombies.
**[observed]** The work merge `FUN_18001d5e0` carries the seven fields forward; worker helper `FUN_1800218e0`
iterates that list with stride `0x1c` and invokes `FUN_18000dca0`.
Zero width and height select a point/search path; positive area dimensions select `FUN_18000e0c0`, which samples
positions, passes target coordinates toward `FUN_180018810` and bounds its outer loop by the requested count.
**[unknown]** Requested count is not a guarantee of successful spawns; physical coordinates, rejection outcomes and
point-path details remain incompletely established.

## n_addZombie

**[observed]** Entry `0x180026d70` writes args0/1/2 as x/y/z at `zombieRecord+0x0/+0x4/+0x8`,
arg3 as a direction byte at `+0xc`, outfit arg4 at `+0x10`, packed flags arg5 at `+0x14`,
path targets args6/7 at `+0x18/+0x1c`, and persistent ID arg8 at `+0x20`; it queues the record through
`FUN_18000be20` at `work+0x88`.
**[observed]** Zero ID invokes `FUN_180018ab0`, whose locked counter increment skips zero; nonzero IDs are retained.
Worker `FUN_18001b850` reads record position/path data and dispatches to virtual/cell storage paths.
**[unknown]** Flag-bit semantics, direction encoding beyond the Java ordinal, persistence across restarts and final
virtual-zombie behaviour are not fully recovered.

## n_registerZombie

**[observed]** Entry `0x180028190` stores args0..5 in the same position/direction/outfit/state offsets;
arg6 selects retained/generated ID at `+0x20`, returned to Java. It writes fixed invalid-target sentinels at
`+0x18/+0x1c` and queues through `work+0x98`.
**[observed]** Worker `FUN_18001b3c0` uses that ID for registered-map lookup/insertion, marking the created native
wrapper as registered; a duplicate path logs and releases the previous registration before reinsertion.
**[unknown]** Counter overflow, global uniqueness and lifetime guarantees are not established.

## n_setSpawnOrigins

**[observed]** Entry `0x180028760` requires a non-null int array whose length is divisible by four, then reads
x/y/width/height groups into `FUN_18001b7a0`, appending `0x10`-byte rectangles through
`DAT_180292fd0+0x120` and increasing its count at `+0x11c`.
**[observed]** The Java initialization path constructs exactly that four-int layout at
`ZombiePopulationManager.java:307–315`. No clearing of the existing list was recovered in this entry.
**[unknown]** Repeated calls must not be assumed to replace the list; downstream spawn-selection weighting and units remain unproven.

## n_loadChunk

**[observed]** Entry `0x180027e70` appends a `0xc`-byte chunk task: integer args0/1 at `+0x0/+0x4`,
and a byte recording whether arg2 equals one at `+0x8`.
The merged task reaches `FUN_18001be00`, which looks up its cell, calls `FUN_18000b310` with the flag and gates
an additional loaded-chunk branch that updates cell bookkeeping.
**[observed]** Java passes true from `addChunkToWorld` and false from `removeChunkFromWorld`
(`ZombiePopulationManager.java:360,367`).
**[unknown]** Chunk coordinates are not established as interchangeable with world-square coordinates or physical distances.

## n_updateRealZombies

**[observed]** Entry `0x180028d30` requires nonnegative count arg0, at least `2*count` ints in arg1 and
`3*count` floats in arg2. It resets the staging count and packs `0x14`-byte records: ID/state at `+0x0/+0x4`,
position x/y/z at `+0x8/+0xc/+0x10`.
**[observed]** Worker `FUN_18001bea0` looks up the registered ID, copies position into
`zombieRecord+0x0/+0x4/+0x8`, copies state to `+0x14`, and calls `FUN_180016f50`.
The work merge only copies this list when its incoming count is nonzero.
**[unknown]** Clearing the staging count with zero does not establish clearing all worker-side registrations or state.

## Reconciliation with the older notes

- **[observed]** [functions-popman.md](functions-popman.md) proposes `PopThread_ProcessSpawnHordeRecord` at
  `0x1800203a0`, described as “consumes one 28-byte spawnHorde record”.
  Fresh decompilation instead reads three integers and updates/removes entries in a different three-int list.
  The seven-field horde path is `FUN_1800218e0 -> FUN_18000dca0`, with the area branch through `FUN_18000e0c0`.
  The older proposed address/role association is contradicted by these readers; it is not reused here.
- **[observed]** [population.md](population.md)'s horde claim “appends a 0x1c-byte record” is confirmed at
  `0x1800288f0`. Its “7 x 32-bit” describes widths; it must not be interpreted as seven integers:
  fresh javap and float stores establish four ints, two floats and an int.
- **[observed]** The older note says “reanimated players and dead zombies are skipped” in real-zombie packing.
  The fresh `packRealZombies` read (`ZombiePopulationManager.java:510–525`) instead excludes zero-ID records;
  dead/reanimated checks only suppress the unregistered warning count in that zero-ID branch.
  A nonzero-ID record is packed without those checks in this method.
  **[unknown]** Filtering of its input collection elsewhere was not traced.
- **[observed]** The older config-to-fields label at `0x18001e9e0` is corroborated by the fresh key comparisons
  and stores above. Its prior “not decompiled” status for config/set-origin/load/register entries is superseded
  for this bounded slice, without claiming anything about historical analysis coverage.
- **[unknown]** Older claims about sound, native file formats, full density/repopulation algorithms and other native
  entries were not revalidated; their mention here does not endorse them.

## What a modder can change and what happens

- **[observed]** The Java sandbox-reload path sends named values to pending typed maps; the worker's config consumer
  applies corresponding fields later. The nine bulk inputs share that mechanism, but have no established current Java caller.
- **[observed]** Horde calls queue rectangle/target/count requests; add/register use distinct queues and preserve or
  allocate persistent IDs. Real-update arrays target existing registered IDs.
- **[observed]** Spawn-origin uploads append rectangle records, and chunk load/unload calls queue a coordinate/flag task.
- **[unknown]** These traces establish destinations, not a mod-safe invocation route, a spawn guarantee, permitted ranges,
  client/server authority, update latency or physical units. No sandbox-setting tuning recipe is runtime-verified.

## Verification and reproducibility

- **[observed]** Nine entries returned successfully under REA/Ghidra 12.1.4. Entry Evidence:
  `ev_474d9073d689a9eae70bd70cdcbcb1ef42e56cbf7aa55b94248342890e66d4fb`.
  Supporting consumer batches include `ev_d3c3b2dfd8139fe0ca0c78bc207d3f41124342b12b022d8400b50382c4d32679`,
  `ev_d32881e457cc26e4b54ec74e0c998f4cb7502c4370c7920340537836b5ece212`, and
  `ev_c8064efcd8c7ae6aa2fcecf4bd4c76887c894c01d1ec2dbf722002f5556afa2d`.
- **[observed]** Descriptor source was fresh `javap -p -s` output, independently parsed into scalar/object/array tokens.
  R0 comparison: **9 natives / 43 argument tokens / 0 mismatches**. Per-native counts are
  9/2/2/7/9/7/1/3/3 in the brief's order; numeric indices are contiguous from zero.
- **[observed]** Three parameter rows were re-derived from instruction listings:
  `n_config` arg3's integer map store at `0x180026f96`;
  `n_spawnHorde` arg4's float load/store at `0x180028973/0x180028993`;
  `n_registerZombie` arg6's zero-ID branch, generated/retained store and returned ID at
  `0x180028227/0x18002822b/0x180028230/0x180028265`. All agreed.
  Listing Evidence: `ev_c812e02b1ccc8414e34b1c857c1c4a29e63a3a8d559ad86de66d26da492a8d4a`,
  `ev_af55f0c631c0979abccd7d5035d5b36c6641449c283be6d26312a46bd63034b6`,
  `ev_15799fe5a2121ea694d6fc4286359b764ec55797176ef4034c6b514ac5840a0c`.
- **[observed]** CSV generation iterations: **2**. The first was deleted, then regenerated from the mapping and
  independently obtained descriptors; both files had SHA256
  `4bc92b4c106cfb796b37062c354c90a98705d1d6d5eb20b3e8e2499fb4640198`.
  Rows sort by qualified native then numeric index; header matches the R6 eight-column header.
  No persistent generator was created outside the four authorized paths.
- **[observed]** Retained bundle `r8-popman-io-evidence.json` and snapshot `r8-popman-io-snapshot.json`
  were saved under the authorized external `codex-scratch` directory; `close_binary` completed.

## Limits

- **[observed]** Exactly these nine manager JNI entry bodies were analyzed. The other 19
  `ZombiePopulationManager` natives are out of scope; support-helper traces do not claim coverage of those entries.
  Only PZPopMan64.dll was selected. No game bodies, disassembly, binary bytes or assets were placed in the repository.
- **[unknown]** No target execution, runtime spawn outcome, numerical unit calibration, full density curve,
  safe parameter range, synchronization guarantee or complete Java/Lua/mod reachability was established.
- **[unknown]** The bulk config's actual invocation route remains UNVERIFIED. A declaration-only source search,
  no declaring-class bytecode invocation and no recovered native code caller do not prove universal absence.
- **[unknown]** Some Ghidra string initializers lack function boundaries; RespawnHours key identity was separately
  checked through decoded initializer references to its literal and key objects. Unresolved dynamic dispatch,
  malformed-array behaviour and exception-tail paths were not tested.
- **[observed]** REA diagnostics identified internal working files under
  `%TEMP%/rea-ghidra-2433e94455d1b0f0d93825ba5f9de61d/`: project directory `project/`,
  logs `ghidra.log` and `script.log`. A matching Temp directory was separately observed.
  This is outside the requested scratch root; explicit retained artifacts use scratch.
  **[unknown]** Cleanup after close was not independently verified.
