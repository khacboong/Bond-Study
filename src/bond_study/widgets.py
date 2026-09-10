from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)
from PySide6.QtGui import (
    QFont, QTextCursor, QKeyEvent, QSyntaxHighlighter,
    QTextCharFormat, QColor, QTextDocument,
)
from PySide6.QtCore import QEvent, Qt, Signal, QRegularExpression


# ============================================================
# Terminal widget (supports input inside terminal)
# ============================================================
class TerminalWidget(QTextEdit):
    line_entered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Program output")
        self.setAcceptRichText(False)

        self._input_enabled = False
        self._prompt_pos = 0

        # Default: output mode (no interaction)
        self.setReadOnly(True)

    # ---------- output helpers ----------
    def append_text(self, text: str):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    # ---------- input mode toggles ----------
    def start_input_mode(self):
        """Allow typing/paste ONLY after prompt."""
        self._input_enabled = True
        self.setReadOnly(False)

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self._prompt_pos = cursor.position()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def end_input_mode(self):
        """Lock the terminal again."""
        self._input_enabled = False
        self.setReadOnly(True)

    # ---------- internal guards ----------
    def _clamp_cursor_to_prompt(self):
        cursor = self.textCursor()
        if cursor.position() < self._prompt_pos:
            cursor.setPosition(self._prompt_pos)
            self.setTextCursor(cursor)

    def _clamp_selection_to_prompt(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            if start < self._prompt_pos:
                # clamp selection start to prompt
                cursor.setPosition(self._prompt_pos)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)

    # ---------- paste guard ----------
    def insertFromMimeData(self, source):
        if not self._input_enabled:
            return
        self._clamp_cursor_to_prompt()
        self._clamp_selection_to_prompt()
        super().insertFromMimeData(source)

    # ---------- mouse guards (stop selecting old output) ----------
    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        if self._input_enabled:
            self._clamp_cursor_to_prompt()
            self._clamp_selection_to_prompt()

    def mouseMoveEvent(self, e: QMouseEvent):
        super().mouseMoveEvent(e)
        if self._input_enabled:
            self._clamp_cursor_to_prompt()
            self._clamp_selection_to_prompt()

    # ---------- key handling ----------
    def keyPressEvent(self, event: QKeyEvent):
        # If not in input mode, completely ignore editing
        if not self._input_enabled:
            event.ignore()
            return

        cursor = self.textCursor()

        # Never allow cursor / selection before prompt
        self._clamp_cursor_to_prompt()
        self._clamp_selection_to_prompt()
        cursor = self.textCursor()

        key = event.key()
        mods = event.modifiers()
        pos = cursor.position()
        has_sel = cursor.hasSelection()
        sel_start = cursor.selectionStart() if has_sel else pos

        # Allow copy always (even from old output)
        if mods == Qt.ControlModifier and key == Qt.Key_C:
            super().keyPressEvent(event)
            return

        # Block Backspace into protected area
        if key == Qt.Key_Backspace:
            if pos <= self._prompt_pos or sel_start < self._prompt_pos:
                return
            super().keyPressEvent(event)
            return

        # Block Delete into protected area
        if key == Qt.Key_Delete:
            if pos < self._prompt_pos or sel_start < self._prompt_pos:
                return
            super().keyPressEvent(event)
            return

        # Home key should jump to prompt, not line start
        if key == Qt.Key_Home:
            cursor.setPosition(self._prompt_pos)
            self.setTextCursor(cursor)
            return

        # Enter = submit current input line
        if key in (Qt.Key_Return, Qt.Key_Enter):
            cursor.movePosition(QTextCursor.End)
            full_text = self.toPlainText()
            user_input = full_text[self._prompt_pos:]
            self.append_text("\n")
            self.end_input_mode()
            self.line_entered.emit(user_input.strip())
            return

        # For any normal typing/paste navigation, just ensure we’re after prompt
        if pos < self._prompt_pos:
            cursor.setPosition(self._prompt_pos)
            self.setTextCursor(cursor)

        super().keyPressEvent(event)

class PythonHighlighter(QSyntaxHighlighter):
    NORMAL_STATE = 0
    IN_TRIPLE_SINGLE = 1
    IN_TRIPLE_DOUBLE = 2

    def __init__(self, document):
        super().__init__(document)

        def fmt(color_hex, bold=False, italic=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color_hex))
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            if italic:
                f.setFontItalic(True)
            return f

        self.formats = {
            "keyword": fmt("#CC7832", bold=True),
            "builtin": fmt("#FFC66D"),
            "number": fmt("#6897BB"),
            "string": fmt("#6A8759"),
            "comment": fmt("#808080", italic=True),
            "decorator": fmt("#BBB529"),
            "classdef": fmt("#A9B7C6", bold=True),
            "funcdef": fmt("#A9B7C6", bold=True),
            "funccall": fmt("#7AA2F7"),
            "methodcall": fmt("#7AA2F7"),
            "self": fmt("#9876AA"),
            "operator": fmt("#A9B7C6"),
        }

        self.keywords = [
            "and", "as", "assert", "break", "class", "continue", "def", "del", "elif", "else",
            "except", "False", "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "None", "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield", "match", "case"
        ]

        self.builtins = [
            "print", "input", "len", "range", "min", "max", "sum", "round", "abs", "int", "float",
            "str", "bool", "list", "dict", "set", "tuple", "open", "type", "isinstance", "enumerate",
            "zip", "map", "filter", "sorted", "reversed", "any", "all", "help", "dir"
        ]

        self.re_single_str = QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'")
        self.re_double_str = QRegularExpression(r"\"[^\"\\]*(\\.[^\"\\]*)*\"")
        self.re_comment = QRegularExpression(r"#.*")

        self.re_decorator = QRegularExpression(r"^\s*@\w+")
        self.re_def = QRegularExpression(r"\bdef\s+([A-Za-z_]\w*)")
        self.re_class = QRegularExpression(r"\bclass\s+([A-Za-z_]\w*)")

        self.re_number = QRegularExpression(r"\b\d+(\.\d+)?\b|\b0x[0-9A-Fa-f]+\b")
        self.re_operator = QRegularExpression(r"[\+\-\*/%]=|==|!=|<=|>=|<|>|\+=|-=|\*=|/=|//=|\*\*|=")

        self.re_funccall = QRegularExpression(r"(?<!\.)\b([A-Za-z_]\w*)(?=\s*\()")
        self.re_methodcall = QRegularExpression(r"\.([A-Za-z_]\w*)(?=\s*\()")

    def _intersects(self, a, b, protected):
        for p0, p1 in protected:
            if a < p1 and b > p0:
                return True
        return False

    def highlightBlock(self, text: str):
        self.setCurrentBlockState(self.NORMAL_STATE)
        protected = []
        n = len(text)

        def add_span(start, end, key):
            if start < 0 or end <= start:
                return
            self.setFormat(start, end - start, self.formats[key])
            protected.append((start, end))

        prev = self.previousBlockState()
        i = 0

        if prev in (self.IN_TRIPLE_SINGLE, self.IN_TRIPLE_DOUBLE):
            delim = "'''" if prev == self.IN_TRIPLE_SINGLE else '"""'
            end_pos = text.find(delim, 0)
            if end_pos == -1:
                add_span(0, n, "string")
                self.setCurrentBlockState(prev)
                return
            add_span(0, end_pos + 3, "string")
            i = end_pos + 3

        while i < n:
            s_pos = text.find("'''", i)
            d_pos = text.find('"""', i)

            if s_pos == -1 and d_pos == -1:
                break
            if s_pos == -1 or (d_pos != -1 and d_pos < s_pos):
                opener = d_pos
                delim = '"""'
                state = self.IN_TRIPLE_DOUBLE
            else:
                opener = s_pos
                delim = "'''"
                state = self.IN_TRIPLE_SINGLE

            close_pos = text.find(delim, opener + 3)
            if close_pos == -1:
                add_span(opener, n, "string")
                self.setCurrentBlockState(state)
                return
            add_span(opener, close_pos + 3, "string")
            i = close_pos + 3

        for re_str in (self.re_single_str, self.re_double_str):
            it = re_str.globalMatch(text)
            while it.hasNext():
                m = it.next()
                a = m.capturedStart()
                b = a + m.capturedLength()
                if not self._intersects(a, b, protected):
                    add_span(a, b, "string")

        it = self.re_comment.globalMatch(text)
        while it.hasNext():
            m = it.next()
            a = m.capturedStart()
            b = a + m.capturedLength()
            if not self._intersects(a, b, protected):
                add_span(a, b, "comment")
                break

        it = self.re_decorator.globalMatch(text)
        while it.hasNext():
            m = it.next()
            a = m.capturedStart()
            b = a + m.capturedLength()
            if not self._intersects(a, b, protected):
                add_span(a, b, "decorator")

        for re_dc, key in ((self.re_def, "funcdef"), (self.re_class, "classdef")):
            it = re_dc.globalMatch(text)
            while it.hasNext():
                m = it.next()
                name_a = m.capturedStart(1)
                name_txt = m.captured(1)
                name_b = name_a + len(name_txt)
                if name_a != -1 and not self._intersects(name_a, name_b, protected):
                    add_span(name_a, name_b, key)

        for word, key in ((self.keywords, "keyword"), (self.builtins, "builtin")):
            for w in word:
                re_w = QRegularExpression(rf"\b{w}\b")
                it = re_w.globalMatch(text)
                while it.hasNext():
                    m = it.next()
                    a = m.capturedStart()
                    b = a + m.capturedLength()
                    if not self._intersects(a, b, protected):
                        add_span(a, b, key)

        re_self = QRegularExpression(r"\bself\b")
        it = re_self.globalMatch(text)
        while it.hasNext():
            m = it.next()
            a = m.capturedStart()
            b = a + m.capturedLength()
            if not self._intersects(a, b, protected):
                add_span(a, b, "self")

        for re_x, key in ((self.re_number, "number"), (self.re_operator, "operator")):
            it = re_x.globalMatch(text)
            while it.hasNext():
                m = it.next()
                a = m.capturedStart()
                b = a + m.capturedLength()
                if not self._intersects(a, b, protected):
                    add_span(a, b, key)

        for re_call, key in ((self.re_methodcall, "methodcall"), (self.re_funccall, "funccall")):
            it = re_call.globalMatch(text)
            while it.hasNext():
                m = it.next()
                name_a = m.capturedStart(1)
                name_txt = m.captured(1)
                name_b = name_a + len(name_txt)

                if name_a == -1 or self._intersects(name_a, name_b, protected):
                    continue
                if name_txt in self.keywords or name_txt in self.builtins:
                    continue

                prefix = text[max(0, name_a - 6):name_a]
                if prefix.endswith("def ") or prefix.endswith("class "):
                    continue

                add_span(name_a, name_b, key)

class CodeEditor(QTextEdit):
    PAIRS = {
        "(": ")",
        "[": "]",
        "{": "}",
        "\"": "\"",
        "'": "'",
        "`": "`",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab_spaces = 4
        self.indent_str = " " * self.tab_spaces

        self.setFont(QFont("Courier New", 20))
        self.highlighter = PythonHighlighter(self.document())

        # ---- IDE-like no-wrap + horizontal scrolling ----
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # ---- placeholder (force visible on dark themes) ----
        self.setPlaceholderText("# Type your Python code here...")

        # If you use dark stylesheet, placeholder can become invisible.
        # Fix by explicitly setting PlaceholderText color in palette.
        pal = self.palette()
        pal.setColor(pal.ColorRole.PlaceholderText, QColor("#6b6b6b"))
        self.setPalette(pal)

        # Also: QTextEdit can keep weird rich-text artifacts; disable them.
        self.setAcceptRichText(False)
        self.find_replace_bar = None

    def set_find_replace_bar(self, bar):
        """Attach the small Find/Replace bar used by the lesson editor."""
        self.find_replace_bar = bar

    @staticmethod
    def _command_modifier(mods):
        """Support Cmd on macOS and Ctrl on Windows/Linux."""
        return bool(mods & (Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier))

    def _replace_selection_with_pair(self, opening, closing):
        cursor = self.textCursor()
        selected = cursor.selectedText()
        start = cursor.selectionStart()

        if selected:
            cursor.insertText(opening + selected + closing)
            cursor.setPosition(start + len(opening))
            cursor.setPosition(start + len(opening) + len(selected), QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.insertText(opening + closing)
            cursor.setPosition(cursor.position() - len(closing))
        self.setTextCursor(cursor)

    def _insert_pair_or_skip(self, typed):
        """Insert a pair and leave the cursor between it, or skip a close."""
        cursor = self.textCursor()
        closing = self.PAIRS[typed]

        if cursor.hasSelection():
            self._replace_selection_with_pair(typed, closing)
            return

        # A quote directly after a backslash is an ordinary character, even
        # when the next character happens to be the auto-created close quote.
        if typed in {"'", '"', "`"} and cursor.position() > 0:
            previous = self.document().characterAt(cursor.position() - 1)
            if previous == "\\":
                cursor.insertText(typed)
                self.setTextCursor(cursor)
                return

        following = self.document().characterAt(cursor.position())
        if typed == closing and following == closing:
            cursor.movePosition(QTextCursor.MoveOperation.Right)
            self.setTextCursor(cursor)
            return

        self._replace_selection_with_pair(typed, closing)

    def _delete_empty_pair(self):
        """Delete both sides when Backspace is between an auto-created pair."""
        cursor = self.textCursor()
        if cursor.hasSelection() or cursor.position() <= 0:
            return False

        before = self.document().characterAt(cursor.position() - 1)
        after = self.document().characterAt(cursor.position())
        if before in self.PAIRS and self.PAIRS[before] == after:
            cursor.setPosition(cursor.position() - 1)
            cursor.setPosition(cursor.position() + 2, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            self.setTextCursor(cursor)
            return True
        return False

    def find_text(self, query, backward=False):
        """Find the next match, wrapping around the document when needed."""
        query = query or ""
        if not query:
            return False

        flags = QTextDocument.FindFlag.FindBackward if backward else QTextDocument.FindFlag(0)
        if self.find(query, flags):
            return True

        cursor = self.textCursor()
        cursor.clearSelection()
        cursor.setPosition(self.document().characterCount() - 1 if backward else 0)
        self.setTextCursor(cursor)
        return self.find(query, flags)

    def replace_current(self, query, replacement):
        cursor = self.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == query:
            cursor.insertText(replacement)
            self.setTextCursor(cursor)
            return True
        return False

    def replace_all(self, query, replacement):
        """Replace all matches in one undoable edit."""
        if not query:
            return 0

        original = self.toPlainText()
        count = original.count(query)
        if count == 0:
            return 0

        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(original.replace(query, replacement))
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        return count

    # ---------- helpers ----------
    def _current_line_text_and_start(self):
        c = self.textCursor()
        block = c.block()
        return block.text(), block.position()

    def _leading_ws_len(self, s: str) -> int:
        i = 0
        while i < len(s) and s[i] == " ":
            i += 1
        return i

    def _indent_or_dedent_selection(self, add=True):
        c = self.textCursor()
        doc = self.document()

        # --- no selection -> IDE behavior ---
        if not c.hasSelection():
            line_text, line_start = self._current_line_text_and_start()
            lead_len = self._leading_ws_len(line_text)
            pos = c.position()

            if add:
                # cursor in leading whitespace? indent whole line
                if pos <= line_start + lead_len:
                    edit = QTextCursor(doc)
                    edit.beginEditBlock()
                    edit.setPosition(line_start)
                    edit.insertText(self.indent_str)
                    edit.endEditBlock()

                    # keep cursor position relative
                    c.setPosition(pos + self.tab_spaces)
                    self.setTextCursor(c)
                else:
                    c.insertText(self.indent_str)
                return

            else:
                # dedent current line only if it has indent
                if line_text.startswith(self.indent_str):
                    edit = QTextCursor(doc)
                    edit.beginEditBlock()
                    edit.setPosition(line_start)
                    edit.setPosition(line_start + len(self.indent_str),
                                     QTextCursor.MoveMode.KeepAnchor)
                    edit.removeSelectedText()
                    edit.endEditBlock()

                    new_pos = max(line_start, pos - self.tab_spaces)
                    c.setPosition(new_pos)
                    self.setTextCursor(c)
                return

        # --- selection -> indent/dedent all selected lines safely ---
        start = c.selectionStart()
        end = c.selectionEnd()

        if end > start:
            end -= 1  # avoid including extra empty last line

        start_block = doc.findBlock(start)
        end_block = doc.findBlock(end)

        edit = QTextCursor(doc)
        edit.beginEditBlock()

        block = start_block
        while block.isValid() and block.position() <= end_block.position():
            line_start = block.position()
            line_text = block.text()

            edit.setPosition(line_start)

            if add:
                edit.insertText(self.indent_str)
            else:
                if line_text.startswith(self.indent_str):
                    edit.setPosition(line_start)
                    edit.setPosition(line_start + len(self.indent_str),
                                     QTextCursor.MoveMode.KeepAnchor)
                    edit.removeSelectedText()
                else:
                    lead_len = self._leading_ws_len(line_text)
                    remove_n = min(self.tab_spaces, lead_len)
                    if remove_n > 0:
                        edit.setPosition(line_start)
                        edit.setPosition(line_start + remove_n,
                                         QTextCursor.MoveMode.KeepAnchor)
                        edit.removeSelectedText()

            block = block.next()

        edit.endEditBlock()

    # ---------- key handling ----------
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        mods = event.modifiers()
        c = self.textCursor()

        # ---- Find / Replace ----
        if self._command_modifier(mods) and not (mods & Qt.KeyboardModifier.AltModifier):
            if key == Qt.Key.Key_F and self.find_replace_bar is not None:
                self.find_replace_bar.open(replace=False)
                event.accept()
                return
            if key == Qt.Key.Key_R and self.find_replace_bar is not None:
                self.find_replace_bar.open(replace=True)
                event.accept()
                return
            if key == Qt.Key.Key_G and self.find_replace_bar is not None:
                self.find_replace_bar.find_next(backward=bool(mods & Qt.KeyboardModifier.ShiftModifier))
                event.accept()
                return

            # Toggle comments for the current line or selected lines.
            if key == Qt.Key.Key_Slash:
                self._toggle_comment()
                event.accept()
                return

        # ---- SMART PAIRS: (), [], {}, quotes and backticks ----
        if not (mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.AltModifier)):
            typed = event.text()
            if typed in self.PAIRS:
                self._insert_pair_or_skip(typed)
                event.accept()
                return

        if key == Qt.Key.Key_Backspace and self._delete_empty_pair():
            event.accept()
            return

        # ---- SMART BACKSPACE: delete 4 spaces as one tab ----
        if key == Qt.Key.Key_Backspace and not c.hasSelection():
            pos = c.position()
            block = c.block()
            line_start = block.position()
            col = pos - line_start

            if col >= self.tab_spaces:
                c2 = self.textCursor()
                c2.setPosition(pos - self.tab_spaces)
                c2.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
                prev = c2.selectedText()

                if prev == self.indent_str:
                    c2.removeSelectedText()
                    return

        # ---- SHIFT+TAB (mac can send Tab+Shift) ----
        if key == Qt.Key.Key_Backtab or (key == Qt.Key.Key_Tab and (mods & Qt.KeyboardModifier.ShiftModifier)):
            self._indent_or_dedent_selection(add=False)
            return

        # ---- TAB ----
        if key == Qt.Key.Key_Tab:
            self._indent_or_dedent_selection(add=True)
            return

        # ---- ENTER auto-indent ----
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            line_text, line_start = self._current_line_text_and_start()
            base_indent = " " * self._leading_ws_len(line_text)
            extra = self.indent_str if line_text.strip().endswith(":") else ""

            super().keyPressEvent(event)
            self.insertPlainText(base_indent + extra)
            return

        super().keyPressEvent(event)

    def _toggle_comment(self):
        """Add or remove a Python comment on the selected/current lines."""
        cursor = self.textCursor()
        doc = self.document()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        if end > start:
            end -= 1

        start_block = doc.findBlock(start)
        end_block = doc.findBlock(end)
        blocks = []
        block = start_block
        while block.isValid() and block.position() <= end_block.position():
            blocks.append(block)
            block = block.next()

        non_empty = [block.text() for block in blocks if block.text().strip()]
        uncomment = bool(non_empty) and all(text.lstrip().startswith("#") for text in non_empty)

        edit = QTextCursor(doc)
        edit.beginEditBlock()
        for block in blocks:
            line = block.text()
            line_start = block.position()
            leading = len(line) - len(line.lstrip(" "))
            edit.setPosition(line_start + leading)
            if uncomment:
                if edit.position() < line_start + len(line) and doc.characterAt(edit.position()) == "#":
                    edit.deleteChar()
                    if doc.characterAt(edit.position()) == " ":
                        edit.deleteChar()
            elif line.strip():
                edit.insertText("# ")
        edit.endEditBlock()


class FindReplaceBar(QFrame):
    """Compact, keyboard-friendly Find/Replace controls for CodeEditor."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setObjectName("findReplaceBar")
        self.setVisible(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self.find_edit = QLineEdit()
        self.find_edit.setObjectName("findInput")
        self.find_edit.setPlaceholderText("Find")
        self.find_edit.setClearButtonEnabled(True)
        self.find_edit.returnPressed.connect(self.find_next)
        layout.addWidget(self.find_edit, 2)

        self.replace_edit = QLineEdit()
        self.replace_edit.setObjectName("replaceInput")
        self.replace_edit.setPlaceholderText("Replace")
        self.replace_edit.returnPressed.connect(self.replace_current)
        self.replace_edit.setVisible(False)
        layout.addWidget(self.replace_edit, 2)

        self.previous_button = QPushButton("‹")
        self.previous_button.setToolTip("Previous match (Shift+Cmd+G)")
        self.previous_button.clicked.connect(lambda: self.find_next(backward=True))
        layout.addWidget(self.previous_button)

        self.next_button = QPushButton("›")
        self.next_button.setToolTip("Next match (Cmd+G)")
        self.next_button.clicked.connect(self.find_next)
        layout.addWidget(self.next_button)

        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_button.setVisible(False)
        layout.addWidget(self.replace_button)

        self.replace_all_button = QPushButton("All")
        self.replace_all_button.setToolTip("Replace all matches")
        self.replace_all_button.clicked.connect(self.replace_all)
        self.replace_all_button.setVisible(False)
        layout.addWidget(self.replace_all_button)

        self.status = QLabel()
        self.status.setObjectName("findStatus")
        layout.addWidget(self.status)

        close_button = QPushButton("×")
        close_button.setToolTip("Close (Esc)")
        close_button.clicked.connect(self.close_bar)
        layout.addWidget(close_button)

        self.find_edit.installEventFilter(self)
        self.replace_edit.installEventFilter(self)

    def open(self, replace=False):
        selected = self.editor.textCursor().selectedText()
        if selected and "\n" not in selected:
            self.find_edit.setText(selected)
        self.replace_edit.setVisible(replace)
        self.replace_button.setVisible(replace)
        self.replace_all_button.setVisible(replace)
        self.show()
        self.find_edit.setFocus()
        self.find_edit.selectAll()
        if self.find_edit.text():
            self.find_next()

    def find_next(self, backward=False):
        found = self.editor.find_text(self.find_edit.text(), backward=backward)
        self.status.setText("Match" if found else "No matches")
        return found

    def replace_current(self):
        query = self.find_edit.text()
        if not self.editor.replace_current(query, self.replace_edit.text()):
            self.find_next()
        else:
            self.status.setText("Replaced")
            self.find_next()

    def replace_all(self):
        count = self.editor.replace_all(self.find_edit.text(), self.replace_edit.text())
        self.status.setText(f"Replaced {count}" if count else "No matches")

    def close_bar(self):
        self.hide()
        self.editor.setFocus()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.close_bar()
                return True

            command = bool(event.modifiers() & (
                Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier
            ))
            if command and event.key() == Qt.Key.Key_R:
                self.open(replace=True)
                return True
            if command and event.key() == Qt.Key.Key_F:
                self.find_edit.setFocus()
                self.find_edit.selectAll()
                return True
            if command and event.key() == Qt.Key.Key_G:
                self.find_next(backward=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
                return True
        return super().eventFilter(watched, event)
