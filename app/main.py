from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from themes.dark_theme import DARK_STYLESHEET


def main() -> None:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("IMMERSE Designer")
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
