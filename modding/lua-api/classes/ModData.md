# ModData

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.world.moddata.ModData` (class)
- Extends: `-`; implements: `-`
- Summary [inferred from member names]: Global mod data tables (shared persistent storage).
- Lua access: static members at the class table (`zombie.world.moddata.ModData` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 0 instance, 10 static, 0 static fields, 0 constructors.

## Static methods

- `add(String tag, KahluaTable table)` -> `void`
- `create()` -> `String`
- `create(String tag)` -> `KahluaTable`
- `exists(String tag)` -> `boolean`
- `get(String tag)` -> `KahluaTable`
- `getOrCreate(String tag)` -> `KahluaTable`
- `getTableNames()` -> `ArrayList<String>`
- `remove(String tag)` -> `KahluaTable`
- `request(String tag)` -> `void`
- `transmit(String tag)` -> `void`
