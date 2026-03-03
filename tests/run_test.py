from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


def main() -> int:
    app = QGuiApplication()
    engine = QQmlApplicationEngine()
    engine.load("./tests/run_test.qml")
    return app.exec()


if __name__ == "__main__":
    main()
