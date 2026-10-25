# Lighting controls: native inputs and destinations

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; jar SHA256 prefix `e1a69eb7`; DLL SHA256 prefix `1866188d` [observed, R0/R4].
Target: `F:\SteamLibrary\steamapps\common\ProjectZomboid\Lighting64.dll`, 609,280 bytes [observed, R4; digest confirmed by REA].

**[observed]** This static pass covers all 15 requested JNI entries, producing 77 parameter rows in
[lighting-io.csv](../modding/data/lighting-io.csv). Argument indices exclude JNIEnv/jclass.
Names come from the decompiled declarations in `zombie/iso/LightingJNI.java:1005–1137`; they are available
`varN` names, not recovered original names. The two long arguments in `addRoomLight` explain the gaps in its names.
**[observed]** Types come from R0's javap-derived descriptors; entry addresses agree with the
[R4 export inventory](lighting-native.md). Placement, state and darkness are separate surfaces below.

## Confidence rubric and field notation

- **[observed]** `high` records a traced argument reaching a concrete field/call with the stated conversion or arithmetic.
  It does not certify a physical unit or prove later simulation outcomes.
- **[inferred]** `medium` records concrete data flow whose higher-level meaning depends on arithmetic interpretation,
  partially understood consumers, or a mixed-purpose array layout; it is not assigned from name similarity alone.
- **[unknown]** `low` records a known write whose ultimate effect remains UNVERIFIED; `[unknown]` means no reliable
  destination was recovered. This slice has 75 high, 0 medium, 1 low and 1 unknown rows.
- **[observed]** `light` denotes the record indexed by ID through `DAT_18008fe80`; `roomLight` uses the separate
  map `DAT_18008fed8`. Their pointer-list heads are `DAT_18008fe60` and `DAT_18008feb8`.
  `torch` is selected from the pointer vector beginning at `DAT_18008ff10`.
- **[observed]** `state` is one of four pointers beginning at `DAT_18008fe20`; `DAT_18008fe40` selects the current
  update state. Its queued-command vector occupies `+0xa8/+0xb0/+0xb8`.
  `playerUpdate` is the payload reached through a type-5 command's `+0x60` pointer;
  `command7` is the queued relocation command itself.
- **[observed]** `darknessBuffer` is the float array selected through the layer descriptor; width is `state+0xc`.
  Offsets are byte offsets from the named record, not recovered C++ member names.
  **[unknown]** Physical units and safe ranges are uncalibrated; physical inputs remain `units=[unknown]`.
- **[observed]** Caller labels such as radius, RGB, direction and fatigue are supported by the Java argument expressions
  at `LightingJNI.java:147–162,299–329,418–429,590–603`, in addition to native stores.
  Java adds 32 to z before the reviewed placement calls; native z must not be assumed to equal Java z.

## configure

**[observed]** Entry `0x180013630` stores arg0 directly in float global `DAT_18008f000`.
**[unknown]** Its downstream consumer and final lighting effect were not recovered; the known write is low confidence for effect.

## playerSet

**[observed]** Entry `0x180014af0` coalesces or allocates a type-5 update for the current state; args0..4 reach payload
`+0x10/+0x14/+0x18/+0x1c/+0x20`, args5..8 become boolean bytes `+0x24/+0x25/+0x27/+0x28`,
and args9..11 reach `+0x30/+0x2c/+0x34`.
**[observed]** The caller supplies position, look-vector components, four flags, fatigue, perception distance and cone input;
a missing current state throws an exception. **[unknown]** Queue-consumer effects on visibility are unproven; this is player
context, rather than light creation or a darkness setter.

## teleport

**[observed]** Entry `0x180017280` uses arg0 as player index 0..3, then coalesces or appends a type-7 command;
args1/2 replace its `+0x8c/+0x90` fields. Invalid index or null state selects an exception path.
**[unknown]** This queues relocation of lighting context; physical movement of a player and the later command consumer
are not established. This belongs to player/world placement context, not light state.

## addLight

**[observed]** Entry `0x180012c00` rejects a duplicate arg0 ID, obtains a light record and links it into the list/map.
Args0..4 write `light+0x0/+0x4/+0x8/+0xc/+0x10`; args5..7 write RGB slots `+0x14/+0x18/+0x1c`;
arg9 writes the active byte `+0x20`.
**[unknown]** No read of arg8 was recovered in either the entry decompilation or instruction listing. The Java caller
supplies a building-local ID, but this pass establishes no native destination or effect for that argument.

## addRoomLight

**[observed]** Entry `0x180012df0` rejects duplicate arg0, creates a room-light record and links its separate list/map;
args0..8 reach `+0x0/+0x8/+0x10/+0x18/+0x1c/+0x20/+0x24/+0x28/+0x2c`.
**[observed]** Caller expressions identify ID, two long building/room IDs, x/y/native-z, width/height and active flag;
the native preserves both 64-bit IDs. **[unknown]** Later room-light coverage rules are unproven.

## addTempLight

**[observed]** Entry `0x180013080` writes args0..7 to the same ID/position/radius/RGB offsets as `addLight`,
forces its active byte on, and stores arg8 in both `light+0x24/+0x28` before linking the record.
**[observed]** The caller derives arg8 from lifetime and frame-rate settings. **[unknown]** Counter decrement timing,
duration units and expiry behaviour were not traced; this entry has no recovered duplicate-ID rejection like `addLight`.

## removeLight

**[observed]** Entry `0x180014d30` uses arg0 to select the light-map record, removes its map/list membership,
and either passes it to `FUN_1800128c0` for recycling or links it to a deferred list according to bytes `light+0x2c..+0x2f`.
**[observed]** An unknown ID selects an exception path. **[unknown]** Immediate rendered disappearance is not proven.

## removeRoomLight

**[observed]** Entry `0x180014f00` uses arg0 to remove room-light map/list membership and either calls
`FUN_180012990` or defers recycling according to bytes `roomLight+0x2d..+0x30`; an unknown ID selects an exception path.
**[unknown]** Downstream invalidation and render timing are not established.

## removeTorch

**[observed]** Entry `0x1800150d0` searches the torch vector by arg0 and clears the matching record's ID at `torch+0x0`;
no match returns without a write.
**[unknown]** It is not an evidenced deletion/free operation, and the downstream meaning of the cleared ID is unproven.

## updateTorch

**[observed]** Entry `0x1800173c0` finds arg0's torch or allocates/appends a record. Args1..10 populate
`torch+0x4..+0x28` in four-byte steps; arg11 becomes boolean byte `+0x2c`, arg12 writes `+0x30`, arg13 writes `+0x34`.
**[observed]** The Java caller supplies position, RGB, two direction components, distance, strength, cone flag, dot and
focusing inputs. **[unknown]** Their downstream attenuation/cone equations and units are not established.

## setLightActive

**[observed]** Entry `0x180015390` looks up arg0 in the light map and writes nonzero arg1 as a boolean at `light+0x20`;
an unknown ID selects an exception path. It changes state without creating a light.
**[unknown]** Later lighting-update timing is unproven.

## setLightColor

**[observed]** Entry `0x180015420` selects arg0's existing light and stores args1/2/3 directly at
`light+0x14/+0x18/+0x1c`; an unknown ID selects an exception path.
**[observed]** These are the same component slots initialized by `addLight`; no clamp is recovered in this entry.
**[unknown]** Colour space, safe ranges and downstream rendered intensity remain unproven.

## setRoomLightActive

**[observed]** Entry `0x1800154c0` selects arg0 in the room-light map and writes boolean arg1 at `roomLight+0x2c`;
an unknown ID selects an exception path. It does not use the ordinary light record's active offset.
**[unknown]** Recalculation and display timing remain unproven.

## getDarkMulti

**[observed]** Entry `0x180013d00` uses arg0 for player state and arg3 for layer stride `0xf0`; args1/2 subtract
layer origins `state+0x138900/+0x138904+0xf0*layer` to select a row-major float through `state+0x138928+0xf0*layer`.
**[observed]** Out-of-grid coordinates or layer above 63 return zero; invalid player/null state select exceptions.
**[unknown]** The layer-origin read precedes the layer-range rejection, so this is not a proven safe arbitrary-index API.
This getter reads darkness data; it does not set a light or write darkness.

## getTargetDarkMulti

**[observed]** Entry `0x180014760` uses the same four argument roles and checks as `getDarkMulti`, but reads the float
buffer pointer at `state+0x138930+0xf0*layer`, rather than `+0x138928`.
**[unknown]** These are distinct buffers; their producer, interpolation relationship and darkness scale are unproven.
The same early layer-origin read limits any claim of safe layer bounds.

## What a modder can change and what happens

- **[observed]** Placement inputs populate ordinary/temporary light, room-light or torch records; player context and
  queued relocation are separate operations. **[unknown]** Position units and when queued changes become visible remain unproven.
- **[observed]** State setters replace ordinary-light RGB/active fields or the separate room-light active field.
  They require an existing ID; ordinary light and room-light maps are distinct.
- **[observed]** Darkness arguments select player/layer/grid locations in two read-only query paths.
  **[unknown]** Changing a query argument is not evidence of changing the world's darkness.
- **[observed]** [R3](native-reachability.md) records three Lua routes in this slice:
  `LuaGlobal.configureLighting -> LuaManager.GlobalObject.configureLighting -> LightingJNI.configure`,
  `IsoRoom.clear -> LightingJNI.removeRoomLight`, and
  `IsoChunkMap.ProcessChunkPos -> LightingJNI.teleport`, all with public representative callers.
  **[unknown]** These routes do not establish a standalone mod-safe placement/colour API or safe lifecycle.
- **[observed]** R3 marks the other 12 routes unknown: `playerSet` has a public representative caller,
  `setLightColor` protected, eight placement/state/removal methods private, and both darkness getters have unknown callers.
  **[unknown]** A visibility label or lack of a recorded route does not prove mod inaccessibility.

## Verification and reproducibility

- **[observed]** REA/Ghidra 12.1.4 returned all 15 scoped entries successfully. Entry batch Evidence:
  `ev_db48ec65a26ce44d44cfddf522be993d7e17ccd9b6d11695d8a0c4ad06b03199`.
- **[observed]** Three parameter rows were independently re-derived from instruction listings:
  `configure` arg0's global float store at `0x180013630`;
  `setLightColor` arg1's store at `0x1800154a9`;
  `addLight` arg5's stack load/store at `0x180012d1f/0x180012d4d`.
  All three agreed with the mapping. Listing Evidence:
  `ev_e7120fd1acdbe044ccb8dc4fa30d03cb2134a3cd2e59392c976dbf6a206ad3c8`,
  `ev_790d9e15d3347cb5f4d6a7412b846418686bbafd6e0d7e73d1cb01ea570e0bde`,
  `ev_20084ebd8f02e6d75a093a30554f7b87afa2ea48fe156bbdfaba02586fe07b71`.
- **[observed]** Every CSV argument token was cross-checked against R0's descriptor by a separate PowerShell pass:
  77 rows, 15 natives, **0 type mismatches**. All scoped descriptors have scalar arguments.
- **[observed]** CSV generation iteration count: **2**, from the parameter mapping and R0 descriptors, sorted by native
  and numeric index. The second file was recreated after deleting the first; both files had SHA256
  `e2f392366d201b094e5624f36605dfbba93c1d7cc2be64007b40fda0b67d08b4`.
  No generator file was added outside this task's two owned repository paths.
- **[observed]** Retained analysis bundle `r5-lighting-evidence.json` and snapshot `r5-lighting-snapshot.json`
  were saved under `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\`; `close_binary` completed.

## Limits

- **[unknown]** No runtime execution, gameplay outcome, physical unit calibration, safe input range, synchronization
  guarantee, network authority or new mod route was established. Record storage is not proof of rendered effect.
- **[unknown]** Queue consumers for player/relocation updates, darkness-buffer producers and the configuration global's
  downstream effect remain UNVERIFIED. The extra `addLight` integer has no reliable native destination in this trace.
- **[observed]** Only `Lighting64.dll` was selected as a REA analysis target. No function bodies, instruction listings,
  game source or binary bytes were placed in the repository.
- **[observed]** A failed lookup exposed REA's actual internal project/log root:
  `C:\Users\zackp\AppData\Local\Temp\rea-ghidra-5f1ebb68babb2bffe7f5c6b8e2a3fdb0\`.
  This is an exception to the requested scratch-only placement; the exposed tools offered no caller-selected internal root.
  The provider describes that project as ephemeral and deleted on close. **[unknown]** Filesystem removal was not independently verified.
