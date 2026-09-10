from __future__ import annotations

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import (
    QFont, QTextCursor, QKeyEvent, QSyntaxHighlighter,
    QTextCharFormat, QColor
)
from PySide6.QtCore import Qt, Signal, QRegularExpression


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
