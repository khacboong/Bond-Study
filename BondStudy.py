"""Launch Bond Study from a checkout using the src layout."""

from __future__ import annotations

import sys
from pathlib import Path


# Keep ``python BondStudy.py`` working without requiring package installation.
SOURCE_DIR = Path(__file__).resolve().parent / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from bond_study.app import main
from bond_study.content import (  # noqa: E402
    LESSON_ICON_KEYS,
    LESSON_ICON_SVGS,
    levels,
    lesson_icon_key,
    lessons,
    lessons_per_page,
    make_lesson,
    make_step,
)
from bond_study.lesson_view import Lesson  # noqa: E402
from bond_study.navigation import Main, PathMenuWidget, PathNodeButton  # noqa: E402
from bond_study.theme import APP_STYLE, apply_card_shadow  # noqa: E402
from bond_study.widgets import CodeEditor, PythonHighlighter, TerminalWidget  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
