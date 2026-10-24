# How Java is exposed to Lua (Project Zomboid, Build 42)

Survey date: 2026-10-24. Source: decompile of `zombie/**` (Vineflower 1.12.0) plus the bundled Kahlua library
(`se/krka/kahlua`). Names and behaviour only; no game code is copied. Tags: **[observed]** read in the decompile,
**[inferred]** deduced from it, **[unknown]** not established.

Companion tables: [`../data/lua-globals.csv`](../data/lua-globals.csv) (759 global functions),
[`../data/exposed-classes.csv`](../data/exposed-classes.csv) (999 whitelisted classes),
[`../data/exposed-methods.csv`](../data/exposed-methods.csv) (declared public members, ~33k rows). Regenerate them
with `modding/tools/extract_exposed.py`.

## The pieces

| Piece | Where | Role |
|---|---|---|
| Kahlua | `se.krka.kahlua.*` (bundled) | The Lua VM (Lua 5.1 semantics) and the Java-binding layer. [observed] |
| `LuaManager.Exposer` | inner class of `zombie.Lua.LuaManager` | Subclass of Kahlua's `LuaJavaClassExposer`; holds the explicit whitelist. [observed] |
| `Exposer.exposeAll()` | same | About 1000 `setExposed(X.class)` calls, then one recursive pass and the global-function pass. [observed] |
| `LuaManager.GlobalObject` | same | Holder of every `@LuaMethod(global = true)` function (the Lua globals such as `getPlayer`). [observed] |
| `@UsedFromLua` / `@HiddenFromLua` | `zombie` package | Marker annotations; see below. [observed] |

## Startup flow [observed]

1. `exposeAll()` adds every class to a `LinkedHashSet` through `setExposed`. This is a **whitelist**: `shouldExpose(Class)`
   returns true only for classes in that set.
2. For each whitelisted class it calls `exposeLikeJavaRecursively(clazz, LuaManager.env)`. That walks the class, its
   interfaces and superclass, the generic types of every declared method's parameters, return and exceptions, every
   declared field's type and each constructor's parameters. Anything reached that is also whitelisted gets exposed.
   Types that are reached but not whitelisted are skipped, so listing a class does not pull in unlisted neighbours.
3. `exposeGlobalFunctions(new GlobalObject())` registers every method annotated `@LuaMethod(global = true)` as a Lua
   global. The Lua name is `@LuaMethod(name = ...)` if given, otherwise the Java method name.
4. Extra non-reflective setup follows: keyboard key constants, mouse button constants, and a calendar helper.

## What a Lua script sees for one exposed class [observed]

For a class `a.b.C`:

- **Static table.** A table at `a.b.C` (nested classes use dots: `a.b.Outer.Inner`), reachable from the global
  environment, plus a short alias at the simple name (`C`) **unless that name is already taken**. When two exposed
  classes share a simple name (for example `Clothing` the inventory class and `ItemKey.Clothing`) only the first
  registered owns the short alias. Use the full path to be safe. [inferred for which one wins; the guard itself is observed]
- `C.class` holds the Java `Class` object (Lua cannot call reflection on it; see Restrictions).
- **Static methods** (public, not `@HiddenFromLua`) go on that table under their Java names.
- **Static fields** (public) are copied onto the table **once, at exposure time**, as plain values. They are
  snapshots, not live links. A static field whose name collides with a method is dropped with a Lua warning.
  Enum constants are public static fields, so `SomeEnum.VALUE` works. [observed]
- **Constructors** (public, class not abstract or interface) are registered as `C.new(...)`. [observed]
- **Instance methods** (public, non-static, not hidden) live in a per-class metatable `__index` table. Calling
  `obj:method(...)` finds them there. The index table of a subclass has the superclass's index table as its own
  metatable, so inherited methods resolve through the chain. [observed]
- **Instance fields are not exposed.** Only static fields and methods are bound. Use getters and setters. [observed]
- `__eq` is wired to Java `equals`, so `a == b` in Lua on two Java objects calls `equals`. [observed]

## Overloads [observed]

Java overloads share one Lua name. The exposer wraps them in a `MultiLuaJavaInvoker` that holds the overload list.
At call time it:

1. Tries each overload whose declared parameter types match the argument types exactly (`matchesArgumentTypes`);
2. if none, tries overloads that match when numbers/primitives are allowed (`matchesArgumentTypesOrPrimitives`);
3. if none, tries the rest in order and takes the first that converts cleanly;
4. otherwise throws `No implementation found for function: name(arg types)`.

Practical consequences: argument count and Lua types decide the overload; passing `nil` where Java expects an
object, or a Lua number where a different-width numeric is expected, can pick an unintended overload. The first
conversion that succeeds wins; there is no "ambiguous call" error. [inferred from the call order]

Argument checks report `expected N arguments, got M` and `Expected a method call but got a function call` when you
write `obj.method()` instead of `obj:method()`. [observed]

## Global functions (`@LuaMethod(global = true)`) [observed]

- 759 annotated methods in `GlobalObject` give 728 distinct Lua names (some names are overloaded, such as
  `triggerEvent`, `instanceItem`, `sendClientCommand`, `ZombRand`).
- Lua-name prefix mix (rounded): `get*` 269, `send*` 75, `is*` 62, `add*` 35, `set*` 26. See the CSV for the list.
- `triggerEvent` as a global lets Lua fire any event by name; see [`events.md`](events.md).
- A few `@LuaMethod` methods exist outside `GlobalObject` (for example on `IsoCell`) **without** `global = true`.
  They only rename the Lua-visible method name and are not globals. [observed]

## `@UsedFromLua` and `@HiddenFromLua` [observed]

- `@HiddenFromLua` on a class, method, field or constructor removes it from exposure. The exposer itself and other
  internals carry it.
- `@UsedFromLua` is a documentation/check marker. In a development build (`Core.IS_DEV`) exposing a non-`java.*`
  class that lacks it throws "Missing @UsedFromLua annotation", which keeps the whitelist and the annotation in
  step. It does not grant exposure by itself; the whitelist does. [observed]

## Restrictions [observed]

- `LuaJavaClassExposer` has a disallow list: `Class`, `ClassLoader` (and subclasses), `Module`, `Runtime`,
  `java.awt.Desktop`, and everything in the `java.lang.invoke` and `java.lang.reflect` packages. Such classes are
  never exposed, even if whitelisted. In debug mode (`Core.debug`) `Method` and `Field` are allowed, which backs a
  small set of debug-only global helpers (`getNumClassFunctions`, `getClassFunction`, `getNumClassFields`,
  `getClassField`, `getClassFieldVal`); they refuse `Class`, `ClassLoader` and `Lookup` arguments and throw outside
  debug mode. So normal Lua cannot use reflection to reach unlisted members.
- Only **public** members are bound.
- Whitelist, not blacklist: a class absent from `exposeAll()` is invisible to Lua even if a listed class returns it
  (you get the object but with no usable methods unless a listed superclass or interface covers them). [inferred]

## Practical rules for mod authors [inferred]

- Prefer methods that exist in `exposed-methods.csv` for the exact class (and its superclass chain). If a name is
  not there, Lua cannot call it.
- Call instance methods with `:`; call statics and constructors with `.`.
- A static constant you read is a snapshot taken when the game started.
- The exposer class has a `definition(obj)` helper annotated as a global, but the only `exposeGlobalFunctions` call
  in the game targets `GlobalObject`, so `definition` is **not** registered as a Lua global. [observed]

## Open items

- Conversion rules between Lua values and Java parameter types (Kahlua `KahluaConverterManager`): not read yet. [unknown]
- Which exposed classes are client-only vs server-only: not established. [unknown]
