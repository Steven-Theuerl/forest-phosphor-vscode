# H1 — Forest Phosphor Theme Test

## H2 — Markdown Feature Showcase

### H3 — All the Things

#### H4 — Getting Granular

##### H5 — Deep Nesting

###### H6 — As Deep as It Goes

---

## Text Formatting

Regular paragraph text sits here. It flows naturally and wraps at whatever column width the editor provides. Nothing special, just prose.

**Bold text** stands out. _Italic text_ leans. **_Bold and italic together_** do both. ~~Strikethrough~~ crosses it out. `inline code` is monospaced and highlighted.

You can also write <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> for keyboard shortcuts, and use ==highlighted text== if the renderer supports it.

Here is a [hyperlink to example.com](https://example.com) and a bare reference: <https://example.com>.

---

## Headings With Inline Code

### The `fetchUser()` Function

### A `type: "success" | "error"` Union

---

## Unordered Lists

- Item one
- Item two
  - Nested item A
  - Nested item B
    - Doubly nested
    - Another deep item
  - Back to first level nesting
- Item three
- Item four

## Ordered Lists

1. First step — clone the repo
2. Second step — install dependencies
3. Third step — run the dev server
   1. Open the terminal
   2. Run `pnpm dev`
   3. Open `localhost:5173`
4. Fourth step — make changes

## Task Lists

- [x] Set up project scaffold
- [x] Configure TypeScript
- [x] Add base theme colors
- [ ] Write tests
- [ ] Publish to marketplace
- [ ] Add dark/light variant toggle

---

## Blockquotes

> A simple blockquote. Good for callouts or pulled quotes from another source.

> Multi-line blockquote.
> Second line of the same quote.
> Third line keeps going.

> **Nested blockquote below:**
>
> > This is a blockquote inside a blockquote. Inception.
> >
> > > And one more level deep.

---

## GitHub-Style Callouts

> [!NOTE]
> This is a note callout. Useful for general supplementary information that is worth pointing out.

> [!TIP]
> This is a tip. Use it to highlight helpful hints or shortcuts the reader might appreciate.

> [!IMPORTANT]
> This is important. Use it for information critical to the user's success.

> [!WARNING]
> This is a warning. Use it to flag something that could cause unexpected behavior or data loss.

> [!CAUTION]
> This is a caution. Use it to warn about potentially risky actions or irreversible consequences.

---

## Code Blocks

### TypeScript

```ts
interface UserSettings {
  notifications: boolean;
  darkMode: boolean;
  language: string;
}

async function fetchUser(id: number): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${id}`);
    const responseData = await response.json();
    return responseData.data as User;
  } catch (fetchError) {
    console.error("Failed to fetch user:", fetchError);
    return null;
  }
}
```

### JavaScript

```js
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(form) {
  const errors = {};
  if (!form.name.trim()) {
    errors.name = "Name is required";
  }
  if (!EMAIL_PATTERN.test(form.email)) {
    errors.email = "Invalid email address";
  }
  return errors;
}
```

### Python

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserSettings:
    notifications: bool = True
    dark_mode: bool = False
    language: str = "en"

def describe_user(name: str, settings: UserSettings) -> str:
    mode = "dark" if settings.dark_mode else "light"
    notif_status = "on" if settings.notifications else "off"
    return f"{name} — {settings.language} — notifs {notif_status} — {mode} mode"
```

### Rust

```rust
#[derive(Debug, Clone)]
pub struct User {
    pub id: u64,
    pub name: String,
    pub email: String,
    pub role: Role,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Role {
    Admin,
    Editor,
    Viewer,
}

impl User {
    pub fn is_admin(&self) -> bool {
        self.role == Role::Admin
    }
}
```

### Shell

```bash
# Install dependencies and start the dev server
pnpm install
pnpm dev

# Build for production
pnpm build && pnpm preview
```

### JSON

```json
{
  "name": "forest-phosphor",
  "version": "1.0.0",
  "theme": {
    "base": "vs-dark",
    "colors": {
      "editor.background": "#1a2e1a",
      "editor.foreground": "#c8e6c8",
      "activityBar.background": "#152515"
    }
  }
}
```

### Diff

```diff
- const errors = writable<Record<string, string>>({});
+ const formErrors = writable<Record<string, string>>({});

- const isAdmin = derived(user, $u => $u?.role === "admin");
+ const isAdmin = derived(user, (currentUser) => {
+   if (currentUser === null) return false;
+   return currentUser.role === "admin";
+ });
```

### Plain Text / No Language

```
This is a plain text code block.
No syntax highlighting applied.
Just raw monospaced text.
```

---

## Tables

### Simple Table

| Name  | Role   | Status   |
| ----- | ------ | -------- |
| Alice | Admin  | Active   |
| Bob   | Editor | Active   |
| Carol | Viewer | Inactive |
| Dave  | Editor | Active   |

### Alignment

| Left-aligned | Center-aligned | Right-aligned |
| :----------- | :------------: | ------------: |
| Apple        |     Banana     |        Cherry |
| 100          |      200       |           300 |
| `true`       |    `false`     |        `null` |

### Complex Table

| Token Type | Scope                  | Hex Color | Usage                        |
| :--------- | :--------------------- | :-------- | :--------------------------- |
| Keyword    | `keyword.control`      | `#6abf6a` | `if`, `return`, `export`     |
| String     | `string.quoted`        | `#a8d8a8` | `"hello"`, template literals |
| Comment    | `comment.line`         | `#4a7a4a` | `// line`, `/* block */`     |
| Function   | `entity.name.function` | `#80d4b0` | Function declarations        |
| Type       | `entity.name.type`     | `#98c8e8` | Interfaces, type aliases     |
| Number     | `constant.numeric`     | `#d4b896` | `42`, `3.14`, `0xff`         |

---

## Horizontal Rules

Three ways to write them:

---

---

---

---

## Images

![Alt text for a placeholder image](https://via.placeholder.com/600x200/1a2e1a/6abf6a?text=Forest+Phosphor)

---

## Footnotes

The theme uses a forest green palette[^1] inspired by phosphor terminal displays[^2].

[^1]: Forest greens range from `#1a2e1a` (deep background) to `#c8e6c8` (foreground text).

[^2]: Phosphor monitors emitted green light on a dark screen, a classic terminal aesthetic.

---

## Definition Lists

Forest Phosphor
: A VS Code color theme using deep green backgrounds and bright green accents.

Phosphor Green
: The iconic `#6abf6a` accent color used for keywords, borders, and interactive elements.

Dark Mode
: The default mode. Background `#1a2e1a`, foreground `#c8e6c8`.

---

## HTML in Markdown

<details>
<summary>Click to expand a hidden section</summary>

This content is hidden by default and revealed on click. Useful for long code samples or optional detail.

```ts
const secret = "only revealed on expand";
```

</details>

<br>

<div align="center">

**Centered block via raw HTML**

`forest-phosphor-vscode`

</div>

---

## Math (KaTeX / MathJax)

Inline math: $E = mc^2$

Block math:

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$

$$
f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
$$

---

## Mixed Nesting

1. **Configure the theme**
   - Open the Command Palette with <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>
   - Type `Color Theme` and press <kbd>Enter</kbd>
   - Select **Forest Phosphor**

2. **Verify token colors**

   Here is an example snippet to verify keyword highlighting:

   ```ts
   export default function greet(name: string): string {
     return `Hello, ${name}!`;
   }
   ```

   > [!TIP]
   > If colors look wrong, reload the window with <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> → `Developer: Reload Window`.

3. **Report issues**
   - Open the [GitHub repo](https://github.com/Steven-Theuerl/forest-phosphor-vscode)
   - File an issue with a screenshot and your VS Code version
   - ~~Send a carrier pigeon~~ Use GitHub Issues

---

## Inline Combos

This sentence has `inline code`, **bold**, _italic_, ~~strikethrough~~, and a [link](https://example.com) all in one line.

> This blockquote has `inline code`, **bold text**, and a [link](https://example.com) inside it.

| Column with `code` | Column with **bold** | Column with _italic_ |
| :----------------- | :------------------- | :------------------- |
| `const x = 1`      | **Primary action**   | _Secondary note_     |
| `let y = 2`        | **Warning state**    | _Optional field_     |
