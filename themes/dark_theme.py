DARK_STYLESHEET = """
QWidget {
    background-color: #11161d;
    color: #d7dde6;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QMainWindow, QFrame#panel, QListWidget, QTreeWidget, QTableWidget, QGraphicsView, QTextEdit, QPlainTextEdit,
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTabWidget::pane, QStackedWidget {
    background-color: #161d26;
    border: 1px solid #243241;
}
QPushButton {
    background-color: #1f2f3f;
    border: 1px solid #2d465d;
    border-radius: 4px;
    padding: 6px 10px;
}
QPushButton:hover { background-color: #254766; }
QPushButton:pressed { background-color: #1a3348; }
QPushButton#accentButton {
    background-color: #1677ff;
    border-color: #2196f3;
    color: white;
}
QLabel#titleLabel {
    font-size: 18px;
    font-weight: 700;
    color: #f2f6fb;
}
QLabel#sectionLabel {
    font-size: 13px;
    font-weight: 700;
    color: #7ec8ff;
}
QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #1a496a;
}
QListWidget::item {
    padding: 8px 10px;
}
QHeaderView::section {
    background-color: #0f141a;
    color: #8db6d8;
    padding: 6px;
    border: 1px solid #22313f;
}
QStatusBar { background-color: #0f141a; }
QSplitter::handle {
    background-color: #1a2330;
}
QToolBar {
    spacing: 6px;
    padding: 4px;
}
QScrollBar:vertical {
    background: #11161d;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #2a3b4b;
    min-height: 20px;
    border-radius: 5px;
}
"""
