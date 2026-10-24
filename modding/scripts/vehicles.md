# Vehicle scripts (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Source: installed `media/scripts/**/*.txt`. Claims are **[observed]** unless
marked **[inferred]** or **[unknown]**. Counts describe source occurrences, not
the vehicle registry after template application and overrides.

## Coverage [observed]

There are **241 vehicle definitions in 173 files**, **77 `template vehicle`
definitions in 70 files**, and **four `vehicleEngineRPM` definitions in one file**.
Files overlap between these groups. Examples are
`generated/vehicles/burntAndSmashedVehicles/burntvehicles.txt`,
`generated/vehicles/professionVehicles/vehicle_pickuptruck_lights_fossoil_template.txt`
and `generated/sounds/vehicles/vehicle_engine_rpm.txt`.

Generate [vehicle-keys.csv](../data/vehicle-keys.csv) with
`python -I modding/tools/survey_components.py`. Columns are
`block_type, key, count, value_shape, notes`. Context paths distinguish
`vehicle/part/container` from a vehicle's own keys. `<block>` rows count
definitions or nested blocks; `<entry>` rows count bare entries. Numeric header
types are grouped as `<number>` and concrete part/passenger/template instance
names are omitted. The companion [component-blocks.csv](../data/component-blocks.csv)
records family totals, file counts and example filenames.

## Outer keys and composition [observed]

Vehicle definitions combine scalar keys, repeated template assignments and nested
blocks. Physical keys include `extents`, `centerOfMassOffset`, `mass`,
`physicsChassisShape`, `engineForce`, `maxSpeed`, `brakingForce`, `wheelFriction`
and suspension/steering fields. Space-separated numeric vectors occur alongside
integer and decimal scalars. Other keys cover textures, seats, repair requirements,
spawn/key behavior and engine RPM selection. The CSV retains exact spelling,
including `template!` as a separate key from `template`.

There are **2,659 `template` assignments** and **186 `template!` assignments**
inside vehicle blocks. Templates have their own rows under `template vehicle`;
they are not mixed with the source counts of the vehicle definitions that use them.
**[unknown]** These occurrence counts do not establish the final number of parts
or the precedence of template copying. See
[parser-keys.md](parser-keys.md#7-vehicle) for the Java-side template handling.

## Nested structure [observed]

Vehicle blocks have 1,304 `part`, 1,155 `area`, 463 `attachment`, 412 `wheel`,
380 `passenger`, 290 `skin`, 241 `model`, 80 `crawlThroughWheel`, 79 `sound`,
22 `physics` and 15 `lightbar` child blocks. Template children are counted
separately in the CSV.

- `model` uses `file`, `offset`, `rotate` and `scale`. These are paths/identifiers
  and numeric transforms; the survey does not load the referenced meshes.
- `wheel` uses `front`, `offset`, `radius` and `width`.
- `physics` has keys such as `extents`, `offset`, `radius` and `rotate`; concrete
  shape names in headers are omitted from the aggregate context path.
- `part` has `area`, `category`, `itemType`, `parent`, `recipes` and other keys.
  Its children can include `lua`, `table`, `container`, `window`, `door`, `model`,
  `anim` and `sound`, depending on the definition/template.
- Part `lua` blocks use `create`, `update` and `use` callback identifiers. Part
  `table` blocks have fields such as `recipes`, `skills`, `requireInstalled` and
  `requireUninstalled`; nested arbitrary tables retain their structural contexts.
- Part `container` uses `capacity` and `test`. This lowercase `capacity` is a
  vehicle-part field, distinct from direct item `Capacity` and fluid components.

**[inferred]** Read the context path as part of a key's meaning. A nested vehicle
`sound` block is not a global `sound` script, and the `model` child is not itself
a module-level `model` definition. Callback names and item identifiers are links
to other systems, not implementations embedded in this CSV.

## RPM scripts and limits [observed / unknown]

The four `vehicleEngineRPM` definitions use `VERSION`; their 20 `data` children
use `gearChange` and `afterGearChange`. Vehicles and templates also use
`engineRPMType`. **[unknown]** This survey does not derive gear-shift behavior,
physical units, defaults, or multiplayer replication from those names and shapes.

**[inferred]** Lexical shapes do not establish accepted Java types or runtime
validity. The structural reader's comma/brace/comment limits are described in
[overview.md](overview.md#limits-and-validation). All data tables contain
identifiers, counts and shapes rather than per-vehicle values.

**[observed]** Three source checks selected with seed `20261024`: 412 wheel
children, 186 `template!` assignments and 241 vehicle blocks. An independent
module-depth scan confirms family block/file counts; all six X4 CSVs reproduce
byte-for-byte. Checks are recorded in `HANDOFF.md`.
