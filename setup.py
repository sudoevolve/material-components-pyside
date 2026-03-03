from __future__ import annotations

from setuptools import find_packages, setup


setup(
    name="material-components-pyside-md3qmlpy",
    version="0.1.0",
    description="PySide6 host for MD3 QML components (ported from C++/QML).",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.6",
        "materialyoucolor>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "md3qmlpy=md3qmlpy.app:run",
        ]
    },
)
