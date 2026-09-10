from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


# ============================================================
# Shared visual language
# ============================================================
APP_STYLE = """
QMainWindow, QWidget {
    background: #F5F6FA;
    color: #20243A;
    font-family: "Arial";
}

/* Text labels should sit directly on the card/background. Components that
   need a surface (pills, badges, lesson labels) override this below. */
QLabel { background: transparent; }

QLabel#eyebrow {
    color: #6C5CE7;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#pageTitle {
    color: #20243A;
    font-size: 28px;
    font-weight: 800;
}

QLabel#pageSubtitle, QLabel#muted {
    color: #777D95;
    font-size: 14px;
}

QLabel#levelTitle {
    color: #20243A;
    font-size: 22px;
    font-weight: 800;
}

QLabel#lessonTitle {
    color: #20243A;
    font-size: 24px;
    font-weight: 800;
}

QLabel#stepDescription {
    color: #555B73;
    font-size: 16px;
    line-height: 1.35em;
}

QLabel#pill {
    background: #ECE9FF;
    color: #5E4DD4;
    border: 1px solid #DCD6FF;
    border-radius: 13px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}

QLabel#brandMark {
    background: #6C5CE7;
    color: white;
    border-radius: 16px;
    font-size: 18px;
    font-weight: 800;
}

QFrame#card, QFrame#lessonCard, QFrame#editorCard, QFrame#consoleCard {
    background: #FFFFFF;
    border: 1px solid #E5E7F0;
    border-radius: 18px;
}

QFrame#editorCard, QFrame#consoleCard {
    border-radius: 14px;
}

QWidget#mapCanvas {
    background: #FFFFFF;
    border: 1px solid #E5E7F0;
    border-radius: 18px;
}

QFrame#sectionHeader {
    background: transparent;
    border: none;
}

QPushButton {
    background: #FFFFFF;
    color: #4E556D;
    border: 1px solid #DDE1EC;
    border-radius: 10px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton:hover {
    background: #F1EFFF;
    border-color: #BDB5FF;
    color: #5E4DD4;
}

QPushButton:pressed { background: #E5E1FF; }
QPushButton:disabled { color: #B8BDCC; background: #F0F1F5; border-color: #E6E8EF; }

QPushButton#primaryButton {
    background: #6C5CE7;
    color: white;
    border: 1px solid #6C5CE7;
}

QPushButton#primaryButton:hover { background: #5E4DD4; border-color: #5E4DD4; }
QPushButton#dangerButton { color: #D65367; }
QPushButton#quietButton { border: none; background: transparent; color: #777D95; }
QPushButton#quietButton:hover { background: #ECE9FF; color: #5E4DD4; }
QPushButton#exampleButton {
    background: #F4F1FF;
    color: #6656D9;
    border: 1px solid #DDD7FF;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#exampleButton:hover { background: #EAE6FF; border-color: #BDB5FF; }

QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
QScrollBar::handle:vertical { background: #D7DAE6; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QSplitter::handle { background: #E3E5ED; }

QTextEdit#codeEditor, QTextEdit#terminal {
    background: #20243A;
    color: #F4F5FA;
    border: none;
    border-radius: 10px;
    padding: 12px;
    selection-background-color: #5145A9;
    selection-color: white;
}

QTextEdit#terminal { background: #171A2A; color: #D8DDF0; }
QLabel#windowCaption { color: #8D93A9; font-size: 12px; font-weight: 700; }
QLabel#terminalStatus { color: #6BD6A7; font-size: 12px; font-weight: 700; }
QLabel#lessonPathLabel {
    color: #4F5570;
    background: #FFFFFF;
    border: 1px solid #E6E8F0;
    border-radius: 12px;
    padding: 9px 13px;
    font-size: 13px;
}
"""


def apply_card_shadow(widget, blur=24, y=8, alpha=28):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y)
    shadow.setColor(QColor(40, 46, 82, alpha))
    widget.setGraphicsEffect(shadow)
