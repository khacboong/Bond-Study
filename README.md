# Bond Study

Bond Study is a desktop Python learning app built with PySide6. It guides
learners through 38 lessons, provides runnable examples, and includes a
syntax-highlighted editor with an interactive output console.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 BondStudy.py
```

The root `BondStudy.py` launcher adds `src/` to Python's import path, so the
project can be run directly without an editable install. The implementation
is organized in `src/bond_study/`:

- `content.py` — lesson content, example comments, and SVG lesson icons
- `theme.py` — shared application styling
- `widgets.py` — editor, syntax highlighter, and terminal widget
- `lesson_view.py` — lesson workspace and code runner
- `navigation.py` — lesson map and main window
- `app.py` — Qt application entry point

## Editor shortcuts

- Type `(`, `[`, `{`, `'`, `"`, or `` ` `` to create a matching pair.
- Type a closing character when it is already next to the cursor to skip over it.
- Press Backspace between an empty pair to remove both characters.
- Select text and type an opening pair character to wrap the selection.
- `Cmd+/` toggles Python comments on the current or selected lines.
- `Cmd+F` opens Find; `Cmd+R` opens Find/Replace.
- `Cmd+G` and `Shift+Cmd+G` move to the next and previous match.
- `Esc` closes the Find/Replace bar and returns focus to the editor.
