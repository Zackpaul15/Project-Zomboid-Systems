# Timed-action family (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Sources: installed Lua action classes and queue implementation. Claims are
**[observed]** unless tagged **[inferred]** or **[unknown]**. Descriptions are
original; no action bodies are copied.

## Family and reference tables [observed]

`ISBaseTimedAction` derives from `ISBaseObject` and is defined in
`shared/TimedActions/ISBaseTimedAction.lua`. The queue is in
`client/TimedActions/ISTimedActionQueue.lua`. Action implementations are spread
through shared/client action folders and domain-specific subfolders, not only
one `TimedActions` directory.

There are **278 derive declarations** reachable from `ISBaseTimedAction` in the
static declaration graph. Reference tables:

- [timed-action-inheritance.csv](../data/timed-action-inheritance.csv): side, file, parent and child for the complete observed family.
- [base-timed-action-methods.csv](../data/base-timed-action-methods.csv): named base-class method declarations.
- [timed-action-hooks.csv](../data/timed-action-hooks.csv): per-method file and declaration counts over the base and its reachable descendants.

**[inferred]** Reachability is based on textual `derive` declarations, not live
class identity. Duplicate declarations are counted separately. Dynamically
created classes or local alias patterns can be missed.

## Queuing and starting [observed]

Construct a concrete action with that class's `new` signature, then pass the
action to `ISTimedActionQueue.add(action)`. The queue resolves the character's
queue through `getTimedActionQueue(action.character)`; it can reject actions
through checks such as `ignoreAction`, sleeping and restrictions while dragging
a corpse. `addToQueue` begins an action immediately if the queue was empty.

The base `begin()` calls `create()`, then starts the character's action.
`create()` adjusts the duration and constructs the Java `LuaTimedActionNew`
wrapper. The base constructor stores the character, initializes interruption
settings and gives `maxTime` an initial value. `getDuration()` returns `maxTime`
in the base implementation, while many subclasses override it.

**[inferred]** A queued action needs a valid character, its required objects and
a duration appropriate to its concrete implementation. Do not call `perform()`
manually as a substitute for queuing. **[unknown]** The source shapes alone do
not specify the engine's complete validity-check or network scheduling sequence.

## Lifecycle hooks and completion [observed]

The base defines `isValidStart`, `isValid`, `waitToStart`, `start`, `update`,
`stop`, `perform`, `getDuration`, `forceCancel` and other helpers. Its `isValid`
body does not supply a useful subclass validation policy. The base `perform`
notifies the queue through `onCompleted(self)`; the base `stop` resets the queue.
The queue removes completed actions and begins the next eligible action.

In the observed family, `perform` is declared in 277 files, `complete` in 236,
`getDuration` in 237, `serverStart` in 52 and `serverStop` in 24. The `complete`
and server-specific methods are subclass conventions, not methods declared in
this base file. For example, `ISCutHair` has separate `perform` and `complete`
implementations: `perform` handles presentation cleanup/queue completion while
`complete` contains changes to the character's hair data.

**[inferred]** For a new B42 action, inspect a current action with similar
effects and preserve its division between presentation, actual state changes,
duration and server hooks. An older tutorial that puts all effects in `perform`
does not describe every action in this install. **[unknown]** The exact side on
which a hook runs and its synchronization contract require engine/network
confirmation; the directory and hook name alone do not prove it.

## Interruption and additional actions [observed / inferred]

**[observed]** The base exposes animation/model helpers, progress accessors,
`addAfter`, `beginAddingActions` and `endAddingActions`. The queue also has
clear/reset/cancel paths and calls `forceCancel` on queued actions not yet started.
`stop`, successful completion and cancellation-before-start are separate paths.

**[inferred]** Clean up resources on every applicable exit path, keep base queue
bookkeeping when overriding `perform`/`stop`, and re-check referenced objects
through the concrete action's validity logic. Queue helpers do not themselves
validate all domain-specific state or grant permission to change a server object.
**[unknown]** This page does not supply a complete runnable action or claim that
every subclass shares the same constructor and return-value contracts.

**[observed]** Action coverage is limited to static declarations and source-level behaviour.
**[unknown]** In-game action execution remains unverified.
