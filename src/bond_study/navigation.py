from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QScrollArea, QVBoxLayout, QWidget
)
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt, Signal
from PySide6.QtSvg import QSvgRenderer

from .content import (
    LESSON_ICON_KEYS, LESSON_ICON_SVGS, lesson_icon_key,
    levels, lessons, lessons_per_page
)
from .lesson_view import Lesson
from .theme import apply_card_shadow


class PathNodeButton(QPushButton):
    """Circular lesson node with an actual SVG topic icon inside it."""
    def __init__(self, icon_svg="", size=110, parent=None):
        super().__init__(parent)
        icon_svg = icon_svg.replace(
            '<svg viewBox="0 0 24 24">',
            '<svg viewBox="0 0 24 24" fill="none" stroke="#171A2A" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">',
        )
        self.icon_renderer = QSvgRenderer(QByteArray(icon_svg.encode("utf-8")), self)
        self.size_px = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCheckable(False)

        # important: stop native button frame
        self.setFlat(True)
        self.setStyleSheet("QPushButton{border:none}")

        # Keep the nodes lifted from the path so the icons are easy to scan.
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(54, 45, 129, 70))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self.rect().adjusted(2, 2, -2, -2)

        pal = self.palette()
        base = pal.color(pal.ColorRole.Button)

        # simple hover/press feedback using system colors
        if self.isDown():
            fill = base.darker(112)
        elif self.underMouse():
            fill = base.lighter(110)
        else:
            fill = base

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(fill)
        p.drawEllipse(r)

        # The topic cue is the focus of the node. The lesson number stays in
        # the label beside it, so the circle reads as an icon rather than a
        # numbered button.
        icon_rect = QRectF(r.adjusted(15, 15, -15, -15))
        self.icon_renderer.render(p, icon_rect)

class PathMenuWidget(QWidget):
    """
    Draws a winding path and places circular lesson buttons along it.
    The larger labels make the path feel like a friendly course map.
    """
    node_clicked = Signal(int)

    def __init__(self, lessons_slice, start_index=0, parent=None):
        super().__init__(parent)
        self.setObjectName("mapCanvas")
        self.lessons_slice = lessons_slice
        self.start_index = start_index

        self.node_size = 74
        self.v_gap = 142
        self.top_pad = 92
        self.side_pad = 160

        self.nodes = []
        self.labels = []
        self.build_nodes()

        self.setMinimumHeight(self.top_pad*2 + len(self.lessons_slice)*self.v_gap)

    def build_nodes(self):
        for b in self.nodes:
            b.deleteLater()
        for l in self.labels:
            l.deleteLater()

        self.nodes.clear()
        self.labels.clear()

        for i, les in enumerate(self.lessons_slice):
            abs_index = self.start_index + i
            icon_key = lesson_icon_key(abs_index)
            btn = PathNodeButton(
                icon_svg=LESSON_ICON_SVGS[icon_key],
                size=self.node_size,
                parent=self,
            )
            pal = btn.palette()
            is_checkpoint = les["title"].startswith("Check Your Progress")
            pal.setColor(QPalette.Button, QColor("#F29D55" if is_checkpoint else "#6C5CE7"))
            btn.setPalette(pal)

            btn.clicked.connect(lambda checked=False, idx=abs_index: self.node_clicked.emit(idx))
            self.nodes.append(btn)

            lab = QLabel(
                f"<b>Lesson {abs_index+1}</b><br>{les['title']}",
                self,
            )
            lab.setObjectName("lessonPathLabel")
            lab.setWordWrap(True)
            self.labels.append(lab)

        self.relayout_nodes()

    def relayout_nodes(self):
        w = self.width()
        center_x = w // 2
        left_x  = center_x - self.side_pad
        right_x = center_x + self.side_pad

        for i, btn in enumerate(self.nodes):
            y = self.top_pad + i * self.v_gap
            x = left_x if i % 2 == 0 else right_x
            btn.move(int(x - self.node_size/2), int(y - self.node_size/2))

            lab = self.labels[i]
            if i % 2 == 0:
                lab.move(int(x + self.node_size*0.7), int(y - 27))
                lab.setAlignment(Qt.AlignmentFlag.AlignLeft)
            else:
                lab_w = 300
                lab.resize(lab_w, 58)
                lab.move(int(x - self.node_size*0.7 - lab_w), int(y - 25))
                lab.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.relayout_nodes()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if len(self.nodes) < 2:
            return

        centers = [btn.geometry().center() for btn in self.nodes]

        path = QPainterPath()
        path.moveTo(centers[0])

        for i in range(1, len(centers)):
            a = centers[i-1]
            b = centers[i]
            ctrl = QPointF((a.x()+b.x())/2, (a.y()+b.y())/2)
            path.quadTo(ctrl, b)

        road_color = QColor("#D8D5F5")
        road_color.setAlpha(220)

        pen = QPen(road_color, 16, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawPath(path)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bond Study · Learn Python")
        self.lesson_window = None

        self.page = 0
        self.total_pages = len(lessons_per_page)

        self.page_starts = [0]
        for n in lessons_per_page[:-1]:
            self.page_starts.append(self.page_starts[-1] + n)

        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(42, 30, 42, 28)
        self.main_layout.setSpacing(20)

        # Dashboard header.
        header = QHBoxLayout()
        header.setSpacing(12)
        brand = QLabel("B")
        brand.setObjectName("brandMark")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFixedSize(42, 42)
        header.addWidget(brand)

        header_copy = QVBoxLayout()
        header_copy.setSpacing(2)
        self.title_label = QLabel("Bond Study")
        self.title_label.setObjectName("pageTitle")
        header_copy.addWidget(self.title_label)
        subtitle = QLabel("A friendly path from your first print statement to real Python projects.")
        subtitle.setObjectName("pageSubtitle")
        header_copy.addWidget(subtitle)
        header.addLayout(header_copy)
        header.addStretch(1)

        self.overall_pill = QLabel("Python learning path")
        self.overall_pill.setObjectName("pill")
        header.addWidget(self.overall_pill, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.addLayout(header)

        level_header = QHBoxLayout()
        level_copy = QVBoxLayout()
        level_copy.setSpacing(2)
        self.level_label = QLabel()
        self.level_label.setObjectName("levelTitle")
        level_copy.addWidget(self.level_label)
        self.level_subtitle = QLabel("Choose a lesson to start practicing")
        self.level_subtitle.setObjectName("muted")
        level_copy.addWidget(self.level_subtitle)
        level_header.addLayout(level_copy)
        level_header.addStretch(1)
        self.progress_label = QLabel()
        self.progress_label.setObjectName("muted")
        level_header.addWidget(self.progress_label, alignment=Qt.AlignmentFlag.AlignBottom)
        self.main_layout.addLayout(level_header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.main_layout.addWidget(self.scroll, 1)

        bottom = QWidget()
        bottom_lay = QHBoxLayout(bottom)
        bottom_lay.setContentsMargins(0, 2, 0, 0)
        bottom_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.previous_button = QPushButton("<")
        self.forward_button = QPushButton(">")

        # no stylesheet on buttons → system theme
        self.previous_button.setText("←")
        self.forward_button.setText("→")
        self.previous_button.setFixedSize(44, 38)
        self.forward_button.setFixedSize(44, 38)

        self.page_label = QLabel()
        self.page_label.setObjectName("pill")
        self.page_label.setContentsMargins(16, 0, 16, 0)

        bottom_lay.addWidget(self.previous_button)
        bottom_lay.addWidget(self.page_label)
        bottom_lay.addWidget(self.forward_button)
        self.main_layout.addWidget(bottom)

        self.previous_button.clicked.connect(self.prev_page)
        self.forward_button.clicked.connect(self.next_page)

        self.build_path_page()
        self.update_page_bar()
        self.resize(1180, 820)
        self.showMaximized()

    def build_path_page(self):
        start = self.page_starts[self.page]
        count = lessons_per_page[self.page]
        end = min(len(lessons), start + count)
        page_lessons = lessons[start:end]

        self.path_widget = PathMenuWidget(page_lessons, start_index=start)
        self.path_widget.node_clicked.connect(self.open_lesson)
        self.scroll.setWidget(self.path_widget)

        self.level_label.setText(f"Level {self.page+1}  ·  {levels[self.page]}")
        self.level_subtitle.setText(
            "Build confidence one small program at a time" if self.page == 0
            else "Keep going — each lesson adds a new tool to your Python kit"
        )
        self.progress_label.setText(f"{start + 1}–{end} of {len(lessons)} lessons")

    def update_page_bar(self):
        self.page_label.setText(f"{self.page + 1}/{self.total_pages}")
        self.previous_button.setEnabled(self.page > 0)
        self.forward_button.setEnabled(self.page < self.total_pages - 1)

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.build_path_page()
            self.update_page_bar()

    def next_page(self):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.build_path_page()
            self.update_page_bar()

    def open_lesson(self, index):
        if self.lesson_window:
            self.lesson_window.close()
        self.lesson_window = Lesson(lessons[index], index, self.open_lesson)
        self.lesson_window.show()
