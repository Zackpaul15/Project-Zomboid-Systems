# Pathfinding (zombie.pathfind + PZPathFind64.dll)

Confidence tags: **[observed]**, **[inferred]**, **[unknown]**. Sources: Vineflower output of `zombie.pathfind`
(90 classes) and Ghidra pseudocode of `PZPathFind64.dll` (x86-64). No game code is copied here.

Function-level names and address ranges: [functions-pathfind.md](functions-pathfind.md).

## Java side

- **[observed]** `PathfindNative.useNativeCode` selects between the native engine and the older Java
  `PolygonalMap2`. Both are fed by `PathFindBehavior2.update`.
- **[observed]** A dedicated Java thread `PathfindNativeThread` owns the task queues (players, aggro zombies and
  everyone else have separate priority queues), pushes world changes to the DLL, and calls the native `findPath`
  synchronously.
- **[observed]** World model sent to native: chunks (`updateChunk` with a ByteBuffer), squares
  (`updateSquare`: 64-bit flag word + 16-bit cost short + sloped-surface data), vehicles
  (`addVehicle`/`teleportVehicle` take a ByteBuffer, `removeVehicle` an id).
- **[observed]** Z levels are offset by +32 in requests (`startZ+32`, `targetZ+32`).

## JNI surface

`initWorld(int,int,int,int,boolean)`, `destroyWorld()`, `freeMemoryAtExit()`, `update()`,
`updateChunk(int,int,int,ByteBuffer)`, `removeChunk(int,int)`,
`updateSquare(int,int,int,int,long,short,int,float,float)`, `addVehicle(ByteBuffer)`, `removeVehicle(int)`,
`teleportVehicle(ByteBuffer)`, `int findPath(ByteBuffer req, ByteBuffer out)` - all **[observed]** as Java
declarations and as DLL exports. Plus `PathfindNativeRenderer_renderNative` / `setDebugOption` for the debug UI.

### `findPath` request buffer [observed, Java writer and native reader agree]

1. 6 floats: startX, startY, startZ+32, targetX, targetY, targetZ+32
2. int moverType: 0 other, 1 player, 2 zombie
3. 8 bool bytes: bNPC, canCrawl, crawling, ignoreCrawlCost, canThump, canClimbFences, hasTarget, canBend
4. int minLevel, int maxLevel
5. 3 bool bytes: bRender, canClimbTallFences, avoidFarmingPlants

### Result buffer

- **[observed]** The Java output buffer is big-endian; the native side byte-swaps when it detects that.
- **[observed]** Layout: u16 node count, then 16 bytes per node (4 x u32).
- **[inferred]** Per node: x, y, z and a flags/type int (Java reads it as path node kind). Not verified in the
  Java reader yet.

## Native internals (PZPathFind64.dll)

- **[observed]** A global `World` instance (`DAT_18014f250`). Null -> `RuntimeException("World::instance is null")`;
  `updateSquare` uses `NullPointerException("World::instance == null")`.
- **[observed]** `findPath` (0x180049060): if the dirty flag (`DAT_18014db20`, set by `updateSquare`) is set, it
  rebuilds derived data first - clears and re-collects sets, rebuilds the chunk index array, bumps a version
  counter (`DAT_18014d560`) and calls `FUN_18002d7b0` on the search engine at `0x18014dac0`. Then it parses the
  request (`FUN_180048930`) and runs `FUN_18002e2d0(engine, request, bRender)`.
  [inferred] Consequence: a burst of `updateSquare` calls is cheap; the cost is paid once on the next `findPath`.
- **[observed]** `updateSquare` (0x18004a7f0): finds the chunk via `World::findChunk(x,y)`, checks the supplied
  chunk version equals the one stored in the chunk (stale updates are dropped), stores flags + cost, and maps
  `slopedSurfaceDirection` (8 = none) through a 12-byte-per-entry table of 3 floats (0x18014d9c0) into the
  square, together with slopedSurfaceHeightMin/Max.
- **[observed]** RTTI classes: `IGoalNode`, `ISearchNode`, `AStar`, `HLAStar`, `HLSearchNode`, `HLGoalNode`,
  `HLLevelTransition`, `HLSlopedSurface`, `HLStaircase`, `SearchNode`, `GoalNode`, `VGAStar`, `dtNode`,
  ClipperLib (`Clipper`, `ClipperBase`, `PolyNode`, `PolyTree`, `clipperException`).
- **[inferred]** The DLL is a C++ port of the Java `VGAStar` (visibility-graph A*) and `HLAStar` (hierarchical
  A* with level transitions, stairs, sloped surfaces); Clipper is used for obstacle polygon union/offset.
  The name `dtNode` suggests Detour-style node bookkeeping.

## Following a path (PathFindBehavior2) [observed]

- Goal types: None, Character, Location, Sound, SitOnFurniture, VehicleAdjacent, VehicleArea, VehicleSeat.
- Progress states: notrunning, notyetfound, found, failed. A request is issued when notrunning; the result is
  polled each update.
- Movement: `closestPointOnPath`, `pathIndex`/`pathNext`, and a `walkingOnTheSpot` check that fails the path when
  the mover is stuck. End reached when `distToEnd <= 0.05`. Returns Working / Failed / Succeeded.
- Vehicle targets use `chooseBestAttackPosition`; a repath delay of 6.25 applies to moving vehicles.
- Zombies run `checkCrawlingTransition` at path corners; sandbox `lore.speed == 1` forces `running = true`.

## Unknowns / next steps

- **[unknown]** The search itself (`FUN_18002e2d0`) and rebuild (`FUN_18002d7b0`): heuristic, tie-breaking, how
  `canBend`, `avoidFarmingPlants` and thump cost enter the cost function.
- **[unknown]** `updateChunk` buffer layout (0x18004a2a0) and the vehicle ByteBuffer layout.
- **[unknown]** Exact meaning of the 4th node int in results.
