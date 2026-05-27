# `.pack` format notes

A `.pack` file is split into named sections. The AMD64 reference currently uses:

```text
.world
.types
.words
.regs
.macros
.rules
```

## Sections

### `.world`

Stores project-level metadata and world options as key/value style entries.

### `.types`

Defines scalar data types used by rules and operands. The AMD64 example defines `b8`, `b16`, `b32` and `b64`.

### `.words`

Defines named byte sequences or symbols used by the architecture description.

### `.regs`

Defines architectural registers and generated sub-register views. The AMD64 example maps `rax` through `r15` and sub-register aliases such as 64-bit, 32-bit, 16-bit and 8-bit views.

### `.macros`

Defines reusable instruction templates. Macro bodies can emit bytes, call other macros and express rule logic.

### `.rules`

Defines public encoding rules. Each rule starts with `need` declarations followed by executable DSL instructions.

## DSL concepts

Common instructions and predicates include:

- `need`: declares required operands or literal fields
- `emit`: appends bytes or fragments to the output
- `switch` / `case`: selects behavior by operand value
- `ON` / `OFF`: conditional execution controls
- `call`: invokes another compiled rule
- `fits`, `exists`, `has_subset`, `iarch`, `narch`: rule predicates
- `strict`, `multiple`, `memskip`, `mark`, `pending`: helper operations for encoding and symbol handling

## Stability

The format is still experimental. Treat these notes as a working reference, not a locked specification.
