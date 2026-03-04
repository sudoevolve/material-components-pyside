from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QIcon, QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine

from md3qmlpy.stylemanager import StyleManager


def run(qml_root: Optional[Path] = None) -> int:
    format_ = QSurfaceFormat()
    format_.setSamples(4)
    QSurfaceFormat.setDefaultFormat(format_)

    app = QGuiApplication([])

    repo_root = Path(__file__).resolve().parents[1]
    icon_env = os.environ.get("MD3QMLPY_WINDOW_ICON")
    icon_path: Optional[Path] = None
    if icon_env:
        icon_path = Path(icon_env)
        if not icon_path.is_absolute():
            icon_path = repo_root / icon_path
    else:
        icon_path = (
            repo_root
            / "md3qmlcpp"
            / "material-components-qml-main"
            / "preview"
            / "app_icon.svg"
        )
    if icon_path is not None and icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    if qml_root is None:
        qml_root = repo_root / "md3qmlcpp" / "material-components-qml-main" / "src"

    engine = QQmlApplicationEngine()
    engine.addImportPath(str(qml_root))

    style_manager = StyleManager()

    root_ctx = engine.rootContext()
    root_ctx.setContextProperty(
        "ProjectSourceDir",
        str(repo_root / "md3qmlcpp" / "material-components-qml-main"),
    )
    root_ctx.setContextProperty("StyleManager", style_manager)

    main_qml = qml_root / "App" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(main_qml)))

    if not engine.rootObjects():
        return 1
    return app.exec()
