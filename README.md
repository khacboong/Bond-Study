# Bond Study

Bond Study is a desktop Python learning app built with PySide6. It guides
learners through 38 lessons, provides runnable examples, and includes a
syntax-highlighted editor with an interactive output console.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 BondStudy.py
```

`BondStudy.py` remains the compatibility entry point. The implementation is
split into the `bond_study/` package:

- `content.py` — lesson content, example comments, and SVG lesson icons
- `theme.py` — shared application styling
- `widgets.py` — editor, syntax highlighter, and terminal widget
- `lesson_view.py` — lesson workspace and code runner
- `navigation.py` — lesson map and main window
- `app.py` — Qt application entry point
