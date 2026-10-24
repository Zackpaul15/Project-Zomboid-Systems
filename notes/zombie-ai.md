# Zombie AI (zombie.ai and zombie.ai.states)

Confidence tags: **[observed]**, **[inferred]**, **[unknown]**. Source: Vineflower output of `zombie.ai`
(99 files). No game code is copied; numbers are constants read from it. Timers marked "30fps" are scaled with
`getThirtyFPSMultiplier`.

## Framework

- **[observed]** `State` / `StateMachine` / `StateManager`; zombie states include `ZombieIdleState`,
  `WalkTowardState`, `PathFindState`, `LungeState`, `ThumpState` (+ others not read yet).

## ZombieGroupManager (rally groups)

- **[observed]** Ticks once per 30 (30fps) ticks. Config from sandbox `zombieConfig`: `rallyGroupSize`,
  `rallyGroupSeparation`, `rallyGroupRadius`, `rallyTravelDistance`.
- **[observed]** Not eligible for a group: group size <= 1, `Core.isZombieGroupSound` off, zombie useless /
  dead / fake-dead / sitting against a wall / has a target / inside a building / reused / reanimated for grapple
  only, or standing in a Forest / DeepForest zone.
- **[observed]** `findNearestGroup`: nearest group on the same Z with size below `rallyGroupSize * idealSizeFactor`
  and within `rallyTravelDistance`.
- **[observed]** An idle leader spreads away from other group leaders every 5 game minutes
  (`lastSpreadOutTime + 0.083333336` hours); members path to a random point within `rallyGroupRadius` of the
  leader. Both use `allowRepathDelay = 400`.
- **[observed]** In singleplayer nothing happens in the first 2 survival hours.

## ZombieIdleState

- **[observed]** Wander interval `Rand(400..1000)`, multiplied by 1.5 when it is not raining. Picks a random
  square within +-4 tiles that is free and calls `pathToLocation` with `allowRepathDelay = 200`.
- **[observed]** In last-stand mode it paths to the nearest living player instead.

## LungeState

- **[observed]** `lungeTimer = 180` on enter, counts down at 30fps; ghost-mode targets zero it. At <= 0,
  `allowRepathDelay = 0`. Faces the vector to the target; if the target location is unknown but a last-seen point
  exists it repaths there.
- **[observed]** Minimum simulation level HALF. Lunge sound is rate limited to 5000 ms.

## Hand-offs to other systems

- **[observed]** Zombie movement requests go through `PathFindBehavior2` (see [pathfinding.md](pathfinding.md)).
- **[observed]** Out-of-area zombies are virtualized into `PZPopMan64` (see [population.md](population.md)); the
  `WalkTowardState` / `PathFindState` distinction decides whether a virtualized zombie keeps its path target.

## Unknowns / next steps

- **[unknown]** `ThumpState`, `StateMachine` transitions, `ZombieSittingState`, attack states, and how senses
  (sight / hearing / smell via sandbox `lore`) pick a target.
- **[unknown]** `sadisticAIDirector` and `RealZombieMap`.
