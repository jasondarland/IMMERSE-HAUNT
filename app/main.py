from themes.dark_theme import DARK_STYLESHEET
from app.main_window import launch
from PySide6.QtWidgets import QApplication


def main() -> None:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("IMMERSE Haunted Designer")
    app.setStyleSheet(DARK_STYLESHEET)
    launch()


if __name__ == "__main__":
    main()
