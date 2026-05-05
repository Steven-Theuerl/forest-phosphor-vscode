# Forest Phosphor

A dark VS Code color theme inspired by old CRT phosphor monitors.

![Forest Phosphor — full editor overview](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/images/vscodeHero.webp)

Forest Phosphor blends the organic warmth of forest greens with the cool glow of phosphor displays. Backgrounds stay low-contrast for long sessions; syntax tokens are assigned roles based on what they _mean_ in code — not just what they are — so structure becomes legible at a glance.

Part of the [Forest Phosphor](https://forestphosphor.dev) family — a coordinated palette across VSCode, Obsidian, and iTerm2.

---

## Design philosophy

Most themes assign color by token type. Forest Phosphor assigns color by **semantic role** — what a token _does_ in the code, not just what grammar category it belongs to. The goal is that after a short adjustment period, you stop reading individual tokens and start reading the shape of code.

The palette is built around three tiers of visual weight:

**Tier 1 — Foreground green ![#A2EBA1](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/A2EBA1_sm.png) `#A2EBA1`**
The language itself. Keywords and operators that appear on nearly every line — `if`, `else`, `for`, `const`, `&&`, `=`, `{}`, `;` — are rendered in the same soft green as plain text. They should be readable, not highlighted.

**Tier 2 — Amber ![#E8A030](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/E8A030_sm.png) `#E8A030`**
Structural declarations. Medium frequency. These mark architectural decisions: where a function begins, what gets imported, where control flows back. `function`, `class`, `return`, `import`, `async`, `await`, `new`.

**Tier 3 — Coral ![#F8906E](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/F8906E_sm.png) `#F8906E`**
Attention signals. Used sparingly. When you see coral, something demands focus: `this`, `self`, `throw`, `break`, `unsafe`. Also used for errors and invalid tokens.

### The object system — a blue gradient

| Color                                                                                                                           | Role                                       | Examples                               |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------------------------- |
| ![#7AF8FF](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/7AF8FF_sm.png) Cyan `#7AF8FF`   | Variables — _what is this thing?_          | `userId`, `response`, `items`          |
| ![#77B0FF](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/77B0FF_sm.png) Blue `#77B0FF`   | Properties and fields — _what's on it?_    | `.displayName`, `.length`, object keys |
| ![#D1CF32](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/D1CF32_sm.png) Yellow `#D1CF32` | Functions and methods — _what does it do?_ | `fetchUser()`, `.map()`, `groupBy()`   |

### The type system — a purple gradient

| Color                                                                                                                           | Role                                         | Examples                                                        |
| ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------- |
| ![#C07AC8](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/C07AC8_sm.png) Purple `#C07AC8` | Concrete shapes — things you instantiate     | `class UserService`, `enum Direction`, decorators               |
| ![#FFB4E2](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/FFB4E2_sm.png) Pink `#FFB4E2`   | Abstract shapes — contracts and descriptions | `interface User`, `type ApiResponse`, `<T>`, `string`, `number` |

### Literal values and special delimiters

**Near-white ![#E8F0E8](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/E8F0E8_sm.png) `#E8F0E8`** is reserved for values that are themselves the data — numbers (`42`, `3.14`), booleans (`true`, `false`), `null`, `undefined` — and for structural delimiters that sit outside normal expression flow: Rust lifetimes (`'a`), template/interpolation braces (`${}`), Svelte's reactive `$:`, labels.

### Nesting depth — a consistent rotation

Bracket pair colorization and JSON/object key colors follow the **same depth rotation**, so closing brackets and their corresponding key always share a color:

| Depth | Swatch                                                                                                         | Color                |
| ----- | -------------------------------------------------------------------------------------------------------------- | -------------------- |
| 1     | ![#77B0FF](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/77B0FF_sm.png) | Blue `#77B0FF`       |
| 2     | ![#D1CF32](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/D1CF32_sm.png) | Yellow `#D1CF32`     |
| 3     | ![#FFB4E2](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/FFB4E2_sm.png) | Pink `#FFB4E2`       |
| 4     | ![#C07AC8](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/C07AC8_sm.png) | Purple `#C07AC8`     |
| 5     | ![#7AF8FF](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/7AF8FF_sm.png) | Cyan `#7AF8FF`       |
| 6     | ![#E8F0E8](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/E8F0E8_sm.png) | Near-white `#E8F0E8` |

Brackets start at near-white and work inward (white → blue → yellow → pink → purple → cyan), so the outermost scope is always the most neutral.

### Comments

Comments are ![#5C8656](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/5C8656_sm.png) `#5C8656` — a muted, mid-forest green rendered in italic. They recede into the background without disappearing entirely. JSDoc/TSDoc tags get a slightly brighter ![#7CBF78](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/7CBF78_sm.png) `#7CBF78`.

---

## Language coverage

Full semantic and TextMate highlighting for:

- **TypeScript / JavaScript / JSX / TSX** — primary language; most thoroughly verified
- **Svelte** — template blocks, directives, component tags, reactive declarations
- **Python** — `self`/`cls`, decorators, f-string delimiters, kwargs, typing builtins, magic methods
- **Rust** — lifetimes, traits, structs/enums, macros, `unsafe`, attributes/derives, primitive types
- **HTML / CSS / Markdown** — tags, attributes, pseudo-classes, at-rules, CSS class/ID selectors
- **JSON / YAML / TOML** — depth-aware key coloring
- **Shell / Bash** — variables, builtins, functions
- **GraphQL** — types, fields
- **Go, C/C++, C#, Java** — structural keywords and type distinctions

---

## Palette reference

| Swatch                                                                                                      | Hex       | Role                                                          |
| ----------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------- |
| ![#A2EBA1](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/A2EBA1.png) | `#A2EBA1` | Foreground — flow keywords, operators, punctuation            |
| ![#73e165](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/73e165.png) | `#73e165` | Strings                                                       |
| ![#7AF8FF](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/7AF8FF.png) | `#7AF8FF` | Variables, macros, enum members                               |
| ![#77B0FF](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/77B0FF.png) | `#77B0FF` | Properties, fields, object keys                               |
| ![#D1CF32](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/D1CF32.png) | `#D1CF32` | Functions and methods                                         |
| ![#C07AC8](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/C07AC8.png) | `#C07AC8` | Classes, enums, structs, decorators                           |
| ![#FFB4E2](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/FFB4E2.png) | `#FFB4E2` | Interfaces, type aliases, generics, primitives                |
| ![#E8A030](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/E8A030.png) | `#E8A030` | Structural keywords — `function`, `class`, `return`, `import` |
| ![#F8906E](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/F8906E.png) | `#F8906E` | Attention — `this`, `throw`, `unsafe`, errors                 |
| ![#E8F0E8](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/E8F0E8.png) | `#E8F0E8` | Literal values — numbers, booleans, `null`                    |
| ![#5C8656](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/5C8656.png) | `#5C8656` | Comments                                                      |
| ![#5AE66A](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/5AE66A.png) | `#5AE66A` | Git additions, terminal green, test pass                      |
| ![#D4A24A](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/colors/D4A24A.png) | `#D4A24A` | Warnings, git modifications                                   |

---

## Install

1. Open **Extensions** in VS Code (`Ctrl+Shift+X` / `Cmd+Shift+X`)
2. Search for **Forest Phosphor**
3. Click **Install**
4. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and select **Preferences: Color Theme**
5. Choose **Forest Phosphor**

---

## Screenshots

### Diff view

![Diff view](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/images/vscodeDiff.webp)

### Integrated terminal

![Integrated terminal](https://raw.githubusercontent.com/Steven-Theuerl/forest-phosphor-vscode/trunk/images/vscodeIntegratedTerminal.webp)

> The terminal screenshot pairs Forest Phosphor with the matching iTerm2 preset. Grab it at [forestphosphor.dev](https://forestphosphor.dev).

---

## Family

- **VSCode** — this theme
- **Obsidian** — [forest-phosphor-obsidian](https://github.com/Steven-Theuerl/forest-phosphor-obsidian)
- **iTerm2** — [forest-phosphor-iterm2](https://github.com/Steven-Theuerl/forest-phosphor-iterm2)

All three share the same hex values; switch between apps without losing the look.

---

## Reporting issues

If you find an unstyled element or a token that doesn't read right, open an issue with a screenshot and the language being highlighted. Themes have long tails; user reports are how those gaps get found.

---

## About

Built by Steven Theuerl (August) ([@Steven-Theuerl](https://github.com/Steven-Theuerl)). The full design system lives at [forestphosphor.dev](https://forestphosphor.dev).

<!-- If you find Forest Phosphor useful and want to support continued work: [Buy me a coffee](https://buymeacoffee.com/your-handle) -->

## License

MIT — see [LICENSE](./LICENSE).
