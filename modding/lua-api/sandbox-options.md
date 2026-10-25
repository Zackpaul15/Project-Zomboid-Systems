# Sandbox options (Project Zomboid, Build 42)

Survey date: 2026-10-24. Source: Java declarations and control flow in `zombie/SandboxOptions.java`, `zombie/config/*ConfigOption.java`,
`zombie/sandbox/*` and the game's `media/lua` (`shared/Sandbox/*.lua`, `client/OptionScreens/*`). Names, shapes and
counts only. Tags: **[observed]**, **[inferred]**, **[unknown]**.

Table of every built-in option: [`../data/sandbox-options.csv`](../data/sandbox-options.csv) (269 rows). Class page for the Lua-visible methods:
[`classes/SandboxOptions.md`](classes/SandboxOptions.md). When the values become available during start-up:
[`lifecycle.md`](lifecycle.md).

CSV columns: `name`, `table`, `short_name`, `type`, `min`, `max`, `java_default`, `apocalypse_value`,
`effective_default`, `string_default_length`, `enum_class`, `translation`, `value_translation`, `settings_page`.
String defaults are recorded by length only (the removal lists are long item lists).

## Overview [observed]

- `SandboxOptions.instance` (also `getSandboxOptions()` in Lua) is a singleton holding an ordered list of options and a
  name index. Each option is a Java field built by a private factory (`newBooleanOption`, `newDoubleOption`,
  `newEnumOption`, `newIntegerOption`, `newStringOption`).
- Two copies of the values exist and are synchronised by hand: the Java option objects and the Lua global table
  **`SandboxVars`**. Lua code in mods reads either one. Writing to `SandboxVars` does **not** change the Java side by
  itself; see "Lua and Java copies" below.
- 269 built-in options in this build: 87 enum, 96 double, 45 boolean, 39 integer, 2 string.
- `SANDBOX_VERSION` is 6; `FIRST_YEAR` is 1993 (start-year enum values count from it).

### Naming and tables [observed]

A name with exactly one `.` is split into a table name and a short name; the table becomes a nested table inside
`SandboxVars`. Everything else sits at the top level of `SandboxVars`.

| Table in `SandboxVars` | Options | Contents |
|---|---|---|
| (top level) | 183 | time, world, loot, vehicles, nature, character, meta, animals, ... |
| `ZombieLore` | 29 | zombie behaviour (speed, sprinters, door opening, memory, sight, hearing, ...) |
| `MultiplierConfig` | 37 | `Global`, `GlobalToggle` and one multiplier per skill |
| `ZombieConfig` | 15 | population multipliers and related scaling |
| `Map` | 4 | `AllowMiniMap`, `AllowWorldMap`, `MapAllKnown`, `MapNeedsLight` |
| `Basement` | 1 | `SpawnFrequency` |

Read it as `SandboxVars.Zombies` for a top-level option or `SandboxVars.ZombieLore.Speed` for a table option.
Mod-added options with a dotted id get the same treatment. [observed]

### Option types [observed]

| Type string (Lua `getType`) | Java class | Value range | Notes |
|---|---|---|---|
| `boolean` | `BooleanSandboxOption` | true/false | parse accepts `true` and `1` |
| `integer` | `IntegerSandboxOption` | `min`..`max` | parsing a decimal string casts to int |
| `double` | `DoubleSandboxOption` | `min`..`max` | |
| `enum` | `EnumSandboxOption` (an integer option) | `1`..`numValues` | stored as the 1-based index; the label is a translation key |
| `string` | `StringSandboxOption` | text | optional maximum length |

Setting an enum or number out of range is rejected: the error is logged and the old value stays. [observed for enum;
for the numeric classes the same shape is expected, not individually read]
Two enum options are backed by Java enum classes (`StrongEnumSandboxOption`): `InjurySeverity` (3 values) and
`DamageToPlayerFromHitByACar` (5 values). Their number of values is the number of constants in the class.

`translation` and `value_translation` columns: an option can name an explicit text key stem. The shown label key is
`Sandbox_<stem or short name>`; tooltips add `_tooltip` and help text `_help`. An enum's value labels are
`Sandbox_<value stem or label stem or short name>_option<N>`. [observed in the code that builds the keys; the strings
themselves live in the translation files]

## Defaults: the effective value is not the Java literal [observed]

The `SandboxOptions` constructor does this, in order:

1. Initialise custom (mod) options: `CustomSandboxOptions.instance.initInstance(this)`.
2. Run `media/lua/shared/defines.lua`.
3. `loadGameFile("Apocalypse")`, which runs `media/lua/shared/Sandbox/Apocalypse.lua` and applies each key found in the
   returned table.
4. `setDefaultsToCurrentValues()`: whatever is now in the options becomes the reset-to-default value.

So the default shown to a player, and what `resetToDefault()` restores, is the **Apocalypse preset** where it names the
option, and the Java literal only for options the preset does not list. This build: 268 of 269 options are named in
the Apocalypse file and **44** of them differ from the Java literal (see `java_default` against `apocalypse_value`
in the CSV). The only option the preset omits is `LootItemRemovalList` (an empty-string default). Use the
`effective_default` column.

## Preset files [observed]

`media/lua/shared/Sandbox/` holds `Apocalypse.lua`, `Extinction.lua`, `Outbreak.lua`, `Rising.lua`,
`SixMonthsLater.lua` and `SandboxVars.lua`.

- A preset is a file that **returns** a table: a version key, then option names as keys, and nested tables for
  `Basement`, `Map`, `ZombieLore`, `ZombieConfig`, `MultiplierConfig`. The four main presets list every option (about
  280 lines); `SixMonthsLater` is a shorter partial preset (139 lines, **old-style** all-capitals version key with
  value 5). The other four use the key spelled `Version`, value 6.
- `SandboxVars.lua` (4 lines) assigns the global `SandboxVars` from the Apocalypse table and calls
  `getSandboxOptions():initSandboxVars()`. A comment in it says the call exists so custom options appear in
  `SandboxVars`.
- `loadGameFile` only applies keys with `fromTable`; it does **not** run the version upgrade step. It reads the file
  from the game's own `media` directory, so a mod cannot add a preset through this call. [observed for the call; whether a
  mod can shadow a vanilla file via the file map is [unknown]] `saveGameFile` only writes in debug mode.
- Missing preset file: `loadGameFile` reports success (nothing applied).

## Lua and Java copies [observed]

| Method (on `getSandboxOptions()`) | Direction | Effect |
|---|---|---|
| `toLua()` | Java to Lua | writes every option into the global `SandboxVars`, creating the nested tables |
| `updateFromLua()` | Lua to Java | runs `fromTable` for every option on the global `SandboxVars`, sets the `GameTime` multiplier bias from the `Speed` option (1.2 first in `LastStand`, then overwritten by the `Speed` switch), sets `VirtualZombieManager.maxRealZombies` (a switch on `Zombies` is computed, then the value is overwritten with 1 on the next line), then calls `applySettings`. The only caller in the decompile is the fallback at the end of `SandboxOptions.load()` (no `map_sand.bin`); vanilla Lua never calls it. |
| `initSandboxVars()` | both | for each option: `fromTable`, then `toTable`. Runs when `SandboxVars.lua` loads, so custom options are added to the table |
| `applySettings()` | Java side | applies start date, minutes per day and start time of day to `GameTime` |

`fromTable` only sets an option whose key is present and accepts a number, boolean or string. [observed]

A mod that writes to `SandboxVars.X` therefore changes only the Lua copy; Java code that reads the Java option (loot,
zombie population, day length, ...) does not see it. To change what the engine uses, set the option object:
`getSandboxOptions():getOptionByName("X"):setValue(v)` (or `set(name, value)`). [inferred; no vanilla example of
`updateFromLua` exists]

Vanilla Lua mostly reads values with `getOptionByName(name):getValue()`; direct `SandboxVars.<Name>` reads are common
in client UI code (for example a shut-off modifier check in the button prompt). [observed]

## Persistence, files and network

| Item | Location | Format |
|---|---|---|
| Per-save | `<save>/map_sand.bin` | binary: magic `SAND`, a build number (249), the version (6), a count, then name and value strings, then the preset name |
| Server | `<cacheDir>/Server/<serverName>_SandboxVars.lua` | Lua text with a version key and comments; created on first server start |
| User presets | `<cacheDir>/Sandbox Presets/<name>.cfg` | key/value config (`ConfigFile`) |
| Game presets | `media/lua/shared/Sandbox/<name>.lua` | see above |

[observed] for all four. `isValidPresetName` rejects a name with `/`, `\`, `:`, `;`, `"` or `.`.

- **Reading a save:** `SandboxOptions.load()` reads `map_sand.bin`, then handles the old-zombies-file migration, then
  `applySettings`, then `toLua`. If the file does not exist it resets to defaults and calls `updateFromLua`. A name that
  is not an option logs an "unknown SandboxOption" error and is skipped. `IsoWorld.init` calls it **only when not a
  multiplayer client**.
- **Writing a save:** `GameWindow.save` writes `map_sand.bin` (see [`lifecycle.md`](lifecycle.md)).
- **Upgrades:** `upgradeOptionValue` has migrations for versions below 3, 4, 5 and 6 (day length, car spawn rate, the
  loot options, recently-survivor vehicles). Text and Lua files go through it; presets loaded by `loadGameFile` do not.
- **Network:** a client uses `sendToServer()`. The server's `receiveSandboxOptions` loads the packet, applies it, calls
  `toLua`, saves the server file and rebroadcasts to every client. A client handles the same packet by loading,
  applying and calling `toLua`. [observed]
- **Dedicated server order:** Lua folders, then the server `_SandboxVars.lua` is loaded (the server exits on a load error),
  old-file handling, `saveServerLuaFile`, `toLua`, then `OnGameBoot`.
- **Debug log:** `GameLoadingState` prints every option as `name value` after loading. [observed]

## Helper getters and derived values [observed]

Named in the class page; behaviour in one line each: `getDayLengthMinutes` converts the day-length enum to minutes;
`getCompostHours`, `getCurrentLootedChance`, `getCurrentDiminishedLootPercentage`, `getCurrentLootMultiplier` (square
and no-argument forms), `getCurrentRatIndex` derive values from several options; `randomWaterShut`,
`randomElectricityShut` and `randomAlarmDecay` map an enum choice to a random day count, which the new-game UI stores
in the `WaterShutModifier`, `ElecShutModifier` and `AlarmDecayModifier` options.

## Adding options from a mod: `media/sandbox-options.txt`

Mods add their own options with a text file in the **same script block syntax** as the other mod script files.

**Where [observed]:** for every active mod, in mod order, **one** file is read: `<versionDir>/media/sandbox-options.txt`
if it exists, otherwise `<commonDir>/media/sandbox-options.txt`. The two are **not merged**; a mod that has a version
folder with its own file must repeat everything. No sample file ships with the game (`media/mods` and
`Workshop/ModTemplate` contain none).

**Syntax [observed]:**

- All lines are joined and comments are stripped before parsing.
- A top-level `VERSION = 1` is required. Otherwise parsing throws "invalid or missing VERSION" (logged by the caller; that mod's
  options are not added).
- Every child block must be of type `option` (case-insensitive) or the file fails with "unknown block type". The block
  id is the option name (a dot in the name makes a nested table).
- Keys:

| Key | Applies to | Required |
|---|---|---|
| `type` | all | yes: `boolean`, `double`, `enum`, `integer` or `string`; any other value logs a warning and skips the option |
| `default` | all | yes. Enums: must be greater than 0 |
| `min`, `max` | `double`, `integer` | yes |
| `numValues` | `enum` | yes, greater than 0 |
| `valueTranslation` | `enum` | no |
| `page` | all | no, but see below |
| `translation` | all | no |

- A string option has no length limit (maximum length -1).
- Options created this way are flagged custom and registered through `SandboxOptions.newCustomOption`.

**Showing them in the UI [observed]:** `ServerSettingsScreen.lua` adds each custom option that has a page name to the
existing sandbox page with that name or creates a new page. An option **without a `page`** is not placed on any page; on
a client or server it logs "WARN:MISSING in SettingsTable: <name>". It still exists, still gets a default, and is still
written into `SandboxVars`.

Vanilla page names in the sandbox settings (from `settings_page` in the CSV): `TimeOptions`, `Zombie`, `Loot`,
`WorldOptions`, `NatureOptions`, `Meta`, `Character`, `Vehicle`, `Animal`, preceded by a presets page. The page title is
looked up as `Sandbox_<page>`.

**Lifecycle [observed]:** custom options are cleared by `SandboxOptions.Reset` and `CustomSandboxOptions.Reset` and
re-created from the files at start-up, on `Core.ResetLua` and on return to the menu. See [`lifecycle.md`](lifecycle.md).

## Vanilla UI notes [observed]

- Default pages (counts of options per page in this build): Character 68, Zombie 47, Loot 37, Meta 24, WorldOptions 24,
  NatureOptions 22, Vehicle 17, Animal 13, TimeOptions 5. **12 built-in options have no entry** in the sandbox pages
  table: `StartYear`, `AlarmDecayModifier`, the six `*LootFactor` options, `Farming`, `PlantAbundance`, `NightLength` and
  `AnimalMetaStatsModifier`. The UI code refers to `StartYear` by name for a special control, and the rest are
  referenced by the preset and Last Stand scenario files, so they may be handled by other code. [unknown which]
- `OptionScreens/SandboxOptions.lua` greys out the `MultiplierConfig` and `Map` options according to their toggle.
- `MainScreen:setDefaultSandboxVars` calls `resetToDefault()` then `toLua()`.
- The admin panel (`ISServerSandboxOptionsUI.lua`) uses `copyValuesFrom`, `set`, `loadPresetFile`, `resetToDefault` and
  `sendToServer`.

## Open items

- **[unknown]** When a multiplayer client's `SandboxVars` first reflects the server's values relative to the events in
  `lifecycle.md`.
- **[unknown]** Whether any code outside the decompile (native or Lua scripts in mods) relies on `updateFromLua`.
- **[unknown]** Which engine systems read the Lua `SandboxVars` copy instead of the Java option objects.
- **[unknown]** The meaning of each option's values: only counts, ranges and defaults are in the CSV; labels live in the
  translation files.
