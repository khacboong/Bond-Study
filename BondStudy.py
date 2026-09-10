"""Compatibility launcher for Bond Study.

The implementation now lives in the ``bond_study`` package. This file keeps
the original ``python BondStudy.py`` command and the old import names working.
"""

from bond_study.content import (
    LESSON_ICON_KEYS,
    LESSON_ICON_SVGS,
    levels,
    lesson_icon_key,
    lessons,
    lessons_per_page,
    make_lesson,
    make_step,
)
from bond_study.lesson_view import Lesson
from bond_study.navigation import Main, PathMenuWidget, PathNodeButton
from bond_study.theme import APP_STYLE, apply_card_shadow
from bond_study.widgets import CodeEditor, PythonHighlighter, TerminalWidget
from bond_study.app import main


if __name__ == "__main__":
    raise SystemExit(main())
