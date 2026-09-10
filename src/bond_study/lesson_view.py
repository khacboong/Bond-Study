from __future__ import annotations

import contextlib
import io
import queue
import subprocess
import sys
import textwrap
import threading
import traceback

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSplitter, QVBoxLayout, QWidget
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal

from .content import lessons
from .widgets import CodeEditor, FindReplaceBar, TerminalWidget
from .theme import apply_card_shadow


# ============================================================
# Lesson Window
# ============================================================
class Lesson(QWidget):
    append_text_signal = Signal(str)
    request_input_signal = Signal(str)

    def __init__(self, lesson_data, lesson_index, open_lesson):
        super().__init__()
        self.lesson_data = lesson_data
        self.lesson_index = lesson_index
        self.open_lesson = open_lesson
        self.steps = lesson_data["steps"]
        self.current_step = 0
        self.worker_process = None

        self.worker_thread = None
        self.input_queue = None
        self.waiting_for_input = False
        self.stop_event = threading.Event()

        self.build_ui()

        self.append_text_signal.connect(self.on_append_text)
        self.request_input_signal.connect(self.on_request_input)
        self.output_edit.line_entered.connect(self.on_line_entered)

        self.load_step(0)
        self.showMaximized()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 24)
        root.setSpacing(18)

        # Familiar top bar: brand, lesson title and a compact step indicator.
        top_bar = QFrame()
        top_bar.setObjectName("sectionHeader")
        top_bar.setMinimumHeight(58)
        top_bar.setMaximumHeight(72)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        back_button = QPushButton("←  Lessons")
        back_button.setObjectName("quietButton")
        back_button.clicked.connect(self.close)
        top_layout.addWidget(back_button)

        brand = QLabel("B")
        brand.setObjectName("brandMark")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFixedSize(34, 34)
        top_layout.addWidget(brand)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(1)
        self.lesson_header = QLabel(self.lesson_data["title"])
        self.lesson_header.setObjectName("lessonTitle")
        self.lesson_header.setMinimumWidth(260)
        title_stack.addWidget(self.lesson_header)
        self.lesson_context = QLabel(f"Lesson {self.lesson_index + 1}  ·  Learn by doing")
        self.lesson_context.setObjectName("muted")
        title_stack.addWidget(self.lesson_context)
        top_layout.addLayout(title_stack)
        top_layout.addStretch(1)

        self.page_label = QLabel()
        self.page_label.setObjectName("pill")
        top_layout.addWidget(self.page_label)
        root.addWidget(top_bar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(10)

        # ---------------- LEFT: lesson content + editor ----------------
        left_panel = QFrame()
        left_panel.setObjectName("lessonCard")
        apply_card_shadow(left_panel)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(24, 22, 24, 24)
        left_layout.setSpacing(14)

        self.description_label = QLabel()
        self.description_label.setObjectName("stepDescription")
        self.description_label.setWordWrap(True)
        left_layout.addWidget(self.description_label)

        editor_header = QHBoxLayout()
        editor_caption = QLabel("YOUR CODE")
        editor_caption.setObjectName("eyebrow")
        editor_header.addWidget(editor_caption)
        editor_header.addStretch(1)
        self.step_hint = QLabel("Edit the example, then run it")
        self.step_hint.setObjectName("muted")
        editor_header.addWidget(self.step_hint)
        self.example_button = QPushButton("＋  Add example code")
        self.example_button.setObjectName("exampleButton")
        self.example_button.clicked.connect(self.insert_example_code)
        editor_header.addWidget(self.example_button)
        left_layout.addLayout(editor_header)

        editor_card = QFrame()
        editor_card.setObjectName("editorCard")
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        self.code_edit = CodeEditor()
        self.code_edit.setObjectName("codeEditor")
        self.code_edit.setFont(QFont("Menlo", 14))
        self.find_replace_bar = FindReplaceBar(self.code_edit, editor_card)
        self.code_edit.set_find_replace_bar(self.find_replace_bar)
        editor_layout.addWidget(self.find_replace_bar)
        editor_layout.addWidget(self.code_edit)
        left_layout.addWidget(editor_card, stretch=1)

        # ---------------- RIGHT: output + actions ----------------
        right_panel = QFrame()
        right_panel.setObjectName("lessonCard")
        apply_card_shadow(right_panel)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(22, 22, 22, 22)
        right_layout.setSpacing(14)

        output_header = QHBoxLayout()
        output_caption = QLabel("OUTPUT")
        output_caption.setObjectName("eyebrow")
        output_header.addWidget(output_caption)
        output_header.addStretch(1)
        self.terminal_status = QLabel("●  Ready")
        self.terminal_status.setObjectName("terminalStatus")
        output_header.addWidget(self.terminal_status)
        right_layout.addLayout(output_header)

        console_card = QFrame()
        console_card.setObjectName("consoleCard")
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(8, 8, 8, 8)
        self.output_edit = TerminalWidget()
        self.output_edit.setObjectName("terminal")
        self.output_edit.setFont(QFont("Menlo", 13))
        console_layout.addWidget(self.output_edit)
        right_layout.addWidget(console_card, stretch=1)

        self.run_button = QPushButton("▶  Run code")
        self.run_button.setObjectName("primaryButton")
        self.stop_button = QPushButton("■  Stop")
        self.stop_button.setObjectName("dangerButton")
        self.prev_button = QPushButton("←  Previous")
        self.next_button = QPushButton("Next  →")

        run_row = QHBoxLayout()
        run_row.setSpacing(8)
        run_row.addWidget(self.run_button, 2)
        run_row.addWidget(self.stop_button, 1)
        right_layout.addLayout(run_row)

        nav_row = QHBoxLayout()
        nav_row.setSpacing(8)
        nav_row.addWidget(self.prev_button)
        nav_row.addWidget(self.next_button)
        right_layout.addLayout(nav_row)

        self.exit_button = QPushButton("Close lesson")
        self.exit_button.setObjectName("quietButton")
        self.exit_button.clicked.connect(self.close)
        right_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # ---------------- ADD PANELS TO SPLITTER ----------------
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # optional starting ratio: left bigger
        splitter.setSizes([700, 430])

        root.addWidget(splitter, stretch=1)

        # ---------------- WIRE BUTTONS ----------------
        self.run_button.clicked.connect(self.run_code)
        self.stop_button.clicked.connect(self.stop_code)
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button.clicked.connect(self.next_step)

    def build_ui_2(self):
        main_layout = QVBoxLayout(self)

        self.page_label = QLabel()
        self.page_label.setWordWrap(True)
        self.page_label.setFont(QFont("Arial", 15))
        main_layout.addWidget(self.page_label)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setFont(QFont("Arial", 20))
        main_layout.addWidget(self.description_label)

        self.code_edit = CodeEditor()
        self.code_edit.setFont(QFont("Courier New", 20))
        #self.code_edit.setPlaceholderText("# Type your Python code here...")

        self.output_edit = TerminalWidget()
        self.output_edit.setFont(QFont("Courier New", 20))

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.code_edit)
        splitter.addWidget(self.output_edit)
        splitter.setSizes([350, 250])
        main_layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.stop_button = QPushButton("Stop")
        self.exit_button = QPushButton("Exit")
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        self.run_button.setFont(QFont("Arial", 25))
        self.stop_button.setFont(QFont("Arial", 25))
        self.exit_button.setFont(QFont("Arial", 25))
        self.prev_button.setFont(QFont("Arial", 25))
        self.next_button.setFont(QFont("Arial", 25))

        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.exit_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        main_layout.addLayout(button_layout)

        self.run_button.clicked.connect(self.run_code)
        self.stop_button.clicked.connect(self.stop_code)
        self.exit_button.clicked.connect(self.close)
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button.clicked.connect(self.next_step)

    def run_qt_in_subprocess(self, code: str):
        # run user code in a clean python process (real terminal behavior)
        self.stop_event.clear()

        # Make sure code has a proper: if __name__ == "__main__": guard
        # (not required, but helps some cases)
        wrapped = textwrap.dedent(code)

        self.worker_process = subprocess.Popen(
            [sys.executable, "-u", "-c", wrapped],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        def pump(pipe):
            for line in iter(pipe.readline, ''):
                self.append_text_signal.emit(line)
            pipe.close()

        threading.Thread(target=pump, args=(self.worker_process.stdout,), daemon=True).start()
        threading.Thread(target=pump, args=(self.worker_process.stderr,), daemon=True).start()

        def wait_done():
            self.worker_process.wait()
            self.worker_process = None
            if not self.stop_event.is_set():
                self.append_text_signal.emit("\n[Program finished]\n")

        threading.Thread(target=wait_done, daemon=True).start()

    def example_code_for_step(self):
        """Return the closest working example that can seed an exercise."""
        for step in reversed(self.steps[:self.current_step]):
            code = step.get("code", "").strip()
            if code:
                return code

        # Checkpoints begin a new lesson without a local example. In that case,
        # use the last working example from the previous lesson.
        for lesson in reversed(lessons[:self.lesson_index]):
            for step in reversed(lesson["steps"]):
                code = step.get("code", "").strip()
                if code:
                    return code
        return ""

    def insert_example_code(self):
        example = self.example_code_for_step()
        if not example:
            return

        current = self.code_edit.toPlainText().strip()
        if not current or current.startswith("# Try it yourself"):
            self.code_edit.setPlainText(example)
        else:
            self.code_edit.setPlainText(current + "\n\n# Previous example\n" + example)
        self.example_button.setVisible(False)
        self.code_edit.setFocus()
        self.step_hint.setText("Example added — edit it to solve the task")

    def load_step(self, i):
        self.current_step = i
        step = self.steps[i]

        page = f"Page {i+1}/{len(self.steps)}"
        self.setWindowTitle(f"Lesson {self.lesson_index + 1}: {self.lesson_data['title']}")
        self.page_label.setText(page)
        self.description_label.setText(step["desc"])
        code = step.get("code", "").strip()
        if code:
            self.code_edit.setPlainText(code)
            self.example_button.setText("＋  Add example code")
            self.example_button.setVisible(False)
            self.step_hint.setText("Edit the example, then run it")
        else:
            self.code_edit.setPlainText(
                "# Try it yourself, or click ‘Add example code’ to start."
            )
            self.example_button.setText("＋  Add example code")
            self.example_button.setVisible(True)
            self.step_hint.setText("Start from the previous working example")
        self.terminal_status.setText("●  Ready")

        self.output_edit.clear()
        self.update_nav_buttons()

    def update_nav_buttons(self):
        last_i = len(self.steps) - 1
        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setText("Next Lesson" if self.current_step == last_i else "Next")

    def prev_step(self):
        if self.current_step == 0:
            return
        self.load_step(self.current_step - 1)

    def next_step(self):
        last_i = len(self.steps) - 1
        if self.current_step == last_i:
            try:
                self.open_lesson(self.lesson_index+1)
            except IndexError:
                self.close()
            return
        self.load_step(self.current_step + 1)

    # -------- terminal helpers --------
    def on_append_text(self, text: str):
        self.output_edit.append_text(text)
        if "[Program finished with error]" in text:
            self.terminal_status.setText("●  Error")
        elif "[Program finished]" in text:
            self.terminal_status.setText("●  Finished")
        elif "[Program stopped]" in text:
            self.terminal_status.setText("●  Stopped")

    def on_request_input(self, prompt: str):
        self.output_edit.append_text(prompt)
        self.waiting_for_input = True
        self.output_edit.start_input_mode()

    def on_line_entered(self, line: str):
        if self.waiting_for_input and self.input_queue:
            self.waiting_for_input = False
            self.output_edit.end_input_mode()
            self.input_queue.put(line)

    # -------- run code --------
    def run_code(self):
        # If a thread or process is already running
        if (self.worker_thread and self.worker_thread.is_alive()) or self.worker_process:
            self.output_edit.append_text("\n[Program is already running]\n")
            return

        code = self.code_edit.toPlainText()
        self.output_edit.clear()

        if not code.strip() or code.lstrip().startswith("# Try it yourself"):
            self.output_edit.append_text(
                "Add example code or write a solution before running this step.\n"
            )
            self.terminal_status.setText("●  Ready")
            return

        self.terminal_status.setText("●  Running")

        # --- detect GUI/Qt code ---
        lower = code.lower()
        looks_like_qt_gui = (
                "pyqt5" in lower or "PySide6" in lower or
                "pyside2" in lower or "pyside6" in lower or
                "qapplication" in lower and "exec" in lower
        )

        if looks_like_qt_gui:
            self.run_qt_in_subprocess(code)
            return

        # ---------- normal (non-gui) path ----------
        self.input_queue = queue.Queue()
        self.stop_event.clear()

        def worker():
            class QtTextStream(io.TextIOBase):
                def __init__(self, signal):
                    super().__init__()
                    self.signal = signal

                def write(self, s):
                    if s:
                        self.signal.emit(s)
                    return len(s)

                def flush(self):
                    pass

            stream = QtTextStream(self.append_text_signal)

            def gui_input(prompt=""):
                if self.stop_event.is_set():
                    raise KeyboardInterrupt()
                self.request_input_signal.emit(prompt)
                while True:
                    if self.stop_event.is_set():
                        raise KeyboardInterrupt()
                    try:
                        return self.input_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue

            import builtins, sys

            original_print = builtins.print

            def guarded_print(*args, **kwargs):
                if self.stop_event.is_set():
                    raise KeyboardInterrupt()
                return original_print(*args, **kwargs)

            builtins.print = guarded_print

            exec_env = {
                "__builtins__": __builtins__,
                "input": gui_input,
            }

            def tracer(frame, event, arg):
                if self.stop_event.is_set():
                    raise KeyboardInterrupt()
                return tracer

            try:
                sys.settrace(tracer)
                with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                    exec(code, exec_env, exec_env)

            except KeyboardInterrupt:
                pass
            except Exception:
                self.append_text_signal.emit(traceback.format_exc())
                self.append_text_signal.emit("\n[Program finished with error]\n")
            else:
                if not self.stop_event.is_set():
                    self.append_text_signal.emit("\n[Program finished]\n")
            finally:
                sys.settrace(None)
                builtins.print = original_print

        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def stop_code(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.stop_event.set()
            if self.waiting_for_input and self.input_queue:
                self.waiting_for_input = False
                self.output_edit.end_input_mode()
                self.input_queue.put("")

        if self.worker_process:
            self.stop_event.set()
            try:
                self.worker_process.terminate()
            except Exception:
                pass
            self.worker_process = None

        self.append_text_signal.emit("\n[Program stopped]\n")
        self.terminal_status.setText("●  Stopped")
