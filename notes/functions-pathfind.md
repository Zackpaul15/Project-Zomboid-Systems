# PZPathFind64.dll function map

Companion to [pathfinding.md](pathfinding.md). Names are **proposed**: the DLL has no loaded PDB, so only JNI
exports and CRT/STL code carry real names. Tags: **[observed]** read in decompiled output, **[inferred]** deduced
from structure, callers or constants, **[unknown]** not read. No game code is reproduced here.

- Binary: `PZPathFind64.dll`, sha256 `4452e035ff024dd373c5bae3a8ec431e82c607312aaf34ac375692448bf897b2`, x86-64, MSVC.
- 4789 internal procedures (`0x180001000`-`0x180117368`); 2537 lie below `0x18009a2b0`, and 464 of those were kept as
  game logic after filtering out Clipper, STL and CRT. Those 464 were decompiled and skimmed.
- Ghidra renames made through REA are ephemeral; this table is the durable record.
- Coverage: the functions below are the ones whose role I could establish with reasonable confidence. The rest of
  the game-logic range is STL instantiations, deque-ring pools and small accessors, grouped in the range map.

## Address-range map

| Range | Contents | Tag |
|---|---|---|
| `0x180001000`-`0x180002e40` | static initialisers, exception vtables | [observed] |
| `0x180002e40`-`0x18000cxxx` | HLAStar / HLSearchNode / HLSlopedSurface / HLStaircase / AStar objects | [inferred] from names in strings and structure |
| `0x18000cc00`-`0x18000d100` | Java glue: ByteBuffer wrapper, exception creation, `assert_no_exception` | [observed] |
| `0x18000d5b0`-`0x18000ef50` | chunk and level classes | [inferred] |
| `0x180010140`-`0x180011d30` | iostream / locale | [observed] |
| `0x180012000`-`0x180022fff` | ClipperLib (polygon clipping / offsetting) plus iostream | [observed] |
| `0x180022fb0`-`0x18004c000` | world, chunk, square, node, AStar and VGAStar logic | [observed] |
| `0x180039e60`-`0x18003d6e0` | ifstream / ofstream and Java-exception glue | [observed] |
| `0x180048cf0`-`0x18004c7b0` | JNI exports and debug-overlay renderers | [observed] |
| `0x18004c9f0`-`0x18004d280` | STL exception types (regex error strings etc.) | [observed] |
| `0x18004d280`-`0x18006e880` | vectorised CRT/STL | [inferred] |
| `0x18006e880`-`0x18009a2b0` | CRT / STL / locale / iostream / regex | [observed] |

## JNI exports (`PathfindNative`)

All [observed] (export names).

| Address | Java native | Notes |
|---|---|---|
| `0x180048cf0` | `addVehicle` | |
| `0x180048f40` | `destroyWorld` | |
| `0x180049060` | `findPath` | rebuilds the search engine first if the dirty flag is set, then parses the request buffer |
| `0x180049d20` | `initWorld` | |
| `0x180049dd0` | `removeChunk` | |
| `0x180049ed0` | `removeVehicle` | |
| `0x18004a180` | `update` | |
| `0x18004a2a0` | `updateChunk` | buffer layout [unknown] |
| `0x18004a7f0` | `updateSquare` | looks up the chunk, then maps slope direction through the 12-byte-per-entry table at `0x18014d9c0` |

## World and chunk access

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x18002ead0` | `World_GetChunk(world, cx, cy)` | chunk lookup (called with engine `0x18014dac0`) | [inferred] |
| `0x18002f280` | `World_GetSquare(world, x, y, z)` | square lookup; returns 0 if the chunk/level is absent | [observed] |
| `0x1800482b0` | `World_GetChunkByChunkXY` | | [inferred] |
| `0x180048310` | `World_FindChunkGridCell(x, y)` | subtracts grid origin, divides by 256, indexes the cell array | [observed] |
| `0x1800483b0` | `World_GetChunkBySquareXY` | converts square to chunk coordinates (shift by 8) | [inferred] |
| `0x1800484f0` | `World_Update` | | [inferred] |
| `0x180047760` | `ChunkGrid_Init(minX, minY, w, h)` | allocates the pointer grid | [inferred] |
| `0x18003c5c0` | `FloorToInt` | | [inferred] |

## Square flag helpers (`0x180037aa0`-`0x180038470`)

Square objects expose x/y/z at `+4/+8/+0xc` and a flag word tested by `0x180037ad0(square, mask)` ([observed]).

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x180037aa0`/`ab0`/`ac0` | `Square_GetZ` / `GetY` / `GetX` | coordinate accessors (order by offset) | [inferred] |
| `0x180037ad0` | `Square_HasFlag(sq, mask)` | | [observed] |
| `0x180037c00` | `Square_IsBlockedSolid` | | [inferred] |
| `0x180037d10`-`0x180038130` | `Square_Is*` family | tests of wall / door / window / stair / fence bits on the square and its neighbour; mask groups listed below | [inferred] |
| `0x180038210`/`0x180038270` | `Square_BlockedFromSouthNeighbour` / `...WestNeighbour` | flag 0x8000 on self, or 0x20000 on the neighbour at y-1 / x-1 | [observed] pattern, [inferred] naming |
| `0x1800382d0`/`0x180038340` | `Square_IsClimbableOverNorth` / `...West` | flag 0x800000 / 0x400000 with no 0x401 on self or neighbour | [inferred] |
| `0x1800383b0`/`0x180038410` | `Square_IsWindowOpenNorth` / `...West` | flag 0x200000 / 0x100000 and no door-test hit | [inferred] |
| `0x1800380a0` / `0x1800380e0` | `Square_IsSolidObject` / `Square_IsDoor` | | [inferred] |
| `0x1800404d0` | `Square_EdgeBlockedByDirection` | checks bits 2/4 for the requested edge | [inferred] |
| `0x1800405d0` | `Square_CanMoveBetween(ctx, from, to, flag)` | 421-line adjacency check combining all the helpers above | [observed] structure |

Flag bits seen in these helpers [inferred]: `0x1` solid, `0x2`/`0x4` west/north wall, `0x38`/`0x1c0` door and window
groups, `0x400` plus `0x800`/`0x1000`, `0x2000`/`0x4000` edge walls, `0x10000`/`0x20000` floor/solid,
`0x40000`/`0x80000` neighbour-edge blocks, `0x100000`-`0x800000` window/climb variants,
`0x1000000`/`0x2000000` fence/window-frame, `0x4000000`/`0x10000000` stair variants.

## Search core

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x180004f70` | `HLAStar_FindPath` | high-level (cluster) search | [inferred] |
| `0x180004a30` | `HLAStar_EdgeCost` | | [inferred] |
| `0x180006710` | `HLAStar_GetNeighbors` | | [inferred] |
| `0x180007e60` / `0x1800080f0` | `HLAStar_ResolveEndpoint` | | [inferred] |
| `0x180009c60` | `Chunk_ComputeEdgeFlags` | | [inferred] |
| `0x18000c6d0` | `AStar_Search` | binary-heap A* | [inferred] |
| `0x180025180` / `0x1800251f0` | `OpenHeap_Push` / `OpenHeap_Pop` | | [inferred] |
| `0x180028c30` / `0x180028e50` | `SearchNode_Alloc` / `SearchNode_Init` | | [inferred] |
| `0x180024110`-`0x1800249a0` | flood-grid and boundary tracing | | [inferred] |
| `0x180027280` | `World_CanWalkStraight` | straight-line walkability test | [inferred] |
| `0x18002d7b0` | `SearchEngine_Rebuild` | called by `findPath` when dirty | [observed] |
| `0x18002d870` | `PathSearch_Segment` | | [inferred] |
| `0x18002e2d0` | `PathSearch_Run` | | [inferred] |
| `0x180041a90` | `AStar_Run` | | [inferred] |

## Visibility graph and geometry (`0x180043000`-`0x180047400`)

This block builds and queries a polygon visibility graph over obstacle outlines (Clipper output) [inferred].

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x180043960` | `VisGraph_LinkNodeToVisible` | connects a node to the nodes it can see, using `VisGraph_CanSee` | [inferred] |
| `0x180044bf0` | `VisGraph_LinkOverlappingBounds` | pairwise bounding-box overlap test between polygons | [observed] pattern |
| `0x180044f80` | `VisGraph_MarkContainedNodes` | flags nodes that fall inside polygons | [inferred] |
| `0x180045930` | `Level_FindObstacleRectAt(x, y, level, margin)` | point-in-rect with margin | [inferred] |
| `0x180045a70` | `VisGraph_Build` | top-level build: per-polygon links, bounds, containment, edge insertion | [inferred] |
| `0x180046080` | `Segments_IntersectParam` | segment-segment intersection by cross products | [observed] |
| `0x180046220` | `VisGraph_FindNearestNode` | | [inferred] |
| `0x180046580` | `VisGraph_Init` | zero-initialises counts | [observed] |
| `0x1800467b0` | `Rect_ContainsAnyObstacle` | | [inferred] |
| `0x180046860` | `Edges_Intersect` | | [observed] |
| `0x1800469e0` | `VisGraph_CanSee(a, b)` | rejects when edges intersect or segment crosses polygon edges | [inferred] |
| `0x180046cf0` | `PtrVector_Remove` | | [inferred] |
| `0x180047390` | `VisGraph_AddEdgeSpan` | | [unknown] |
| `0x180038570` | `Square_NeighbourByOffset(dx, dy, dz)` | offsets in -1..1, not all zero | [observed] |

## 2D polygon helpers (`0x1800386a0`-`0x180039680`)

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x1800386a0` | `Polygon_ContainsPoint` | AABB prefilter then `Polygon_PointLocation` | [observed] |
| `0x180038720` | `Triangle_ContainsPoint` | sign-of-cross-product test | [observed] |
| `0x180038840` | `Segment_ClosestPoints` | closest points of two segments | [inferred] |
| `0x180038c60` / `0x180038d40` / `0x180038e60` | `ClosestPointOnSegment*` | squared distance to the nearest edge point, keeps the minimum | [observed] |
| `0x180038f40` / `0x180038fe0` | `Polygon_ClosestPoint` / `Polygon_ClosestPointAny` | iterate outline plus holes (stride 0x28) | [observed] |
| `0x180039080` / `0x180039140` | `PolygonWithHoles_PointLocation` / `Polygon_PointLocation` | returns 0 outside, 1 inside, 2 boundary | [inferred] |
| `0x180039310` | `Segment_PointWithinDistance` | | [observed] |
| `0x180039680` | `PolygonWithHoles_SegmentInside` | segment test plus midpoint location | [inferred] |

## Pools and singletons

Deque-ring free-list pools, one per object type [observed]: allocation pops the front of the ring or `operator_new`s
a fresh block and bumps a counter; release pushes back; a teardown routine frees every block and the ring.

| Allocator | Object size | Teardown | Tag |
|---|---|---|---|
| `0x18003e660` | 0xa8 | `0x18003e740` | [observed] |
| `0x18003ede0` | 0x18 | `0x18003ef00` | [observed] |
| `0x18003fbb0` | 0x28 | `0x18003fc10` | [observed] |
| `0x1800445f0` | 0x90 | `0x180045110` | [observed] |
| `0x180038470` | 0x10 | | [observed] |

What each pool holds is [inferred] only (path nodes, polygon nodes, edges, clusters). Roles are not pinned down.

## Utility and runtime

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x18003afb0` | `Mt19937_Next` | Mersenne-Twister generator (global state `0x18014dbd0`) | [observed] |
| `0x18003b8a0` / `0x18003b960` / `0x18003ba20` | `Rand_IntBelow` / `Rand_IntRange` / `Rand_FloatRange` | | [inferred] |
| `0x18003b7a0` | `Java_InitStringHelpers` | caches `String.getBytes` and the `<init>([B,String)` constructor, charset "UTF-8" | [observed] |
| `0x18003b6d0` | `Java_StringToCString` | | [inferred] |
| `0x18000cc00` | `ByteBuffer_Wrap` | | [inferred] |
| `0x180048930` | `ByteBuffer_ReadInt` | | [inferred] |
| `0x18000cdb0` | `NewJavaException` | | [inferred] |
| `0x18003a7c0` | `ThrownJavaException` | | [inferred] |
| `0x18000d100` | `AssertNoJavaException` | | [inferred] |
| `0x1800489e0` | `Java_GetEnvAttachThread` | thread-local `JNIEnv`, attaches on first use | [observed] |
| `0x180048c50` | `Java_LogToJava` | logs through a cached Java method | [inferred] |
| `0x18000f030` | `PathLog` | logger on `DAT_18014f6d0` | [inferred] |

## Debug overlay

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x18004ae50` | `Debug_IsOptionEnabled(name)` | looks up a string flag | [inferred] |
| `0x18004af00` | `Debug_RenderPaths` | | [inferred] |
| `0x18004bd10` | `Debug_RenderClusters` | gated by `Pathfind.Render.Clusters`, `Pathfind.Render.ChunkRegions`, `Pathfind.PathToMouse.RenderSuccessors` | [observed] strings |

## Standard-library sorts (instantiations)

`0x180041b80`, `0x180041cd0`, `0x180041eb0`, `0x180041f90`, `0x180042320`, `0x1800424c0`, `0x1800428c0` are
introsort pieces (insertion sort, heap build/adjust, median-of-3, partition) on int arrays and 32-byte float-keyed
records [observed]. `0x180042cb0` is an array-construct loop helper.

## Boilerplate (not documented per function)

| Range | Contents |
|---|---|
| ClipperLib `0x180012000`-`0x180022fff` | polygon clipper and offsetter, plus wrappers around it |
| filebuf / ifstream / ofstream `0x180039e60`-`0x18003d6e0` | MSVC iostream |
| CRT / STL / locale / regex `0x18004d280` upward | runtime library |
