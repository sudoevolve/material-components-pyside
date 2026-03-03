from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot, Qt, QUrl
from PySide6.QtGui import QColor, QGuiApplication, QImage


@dataclass(frozen=True)
class _SchemeKeyMap:
    token: str
    qml_key: str


_SCHEME_KEYS: tuple[_SchemeKeyMap, ...] = (
    _SchemeKeyMap("primary", "primary"),
    _SchemeKeyMap("onPrimary", "onPrimaryColor"),
    _SchemeKeyMap("primaryContainer", "primaryContainer"),
    _SchemeKeyMap("onPrimaryContainer", "onPrimaryContainerColor"),
    _SchemeKeyMap("secondary", "secondary"),
    _SchemeKeyMap("onSecondary", "onSecondaryColor"),
    _SchemeKeyMap("secondaryContainer", "secondaryContainer"),
    _SchemeKeyMap("onSecondaryContainer", "onSecondaryContainerColor"),
    _SchemeKeyMap("tertiary", "tertiary"),
    _SchemeKeyMap("onTertiary", "onTertiaryColor"),
    _SchemeKeyMap("tertiaryContainer", "tertiaryContainer"),
    _SchemeKeyMap("onTertiaryContainer", "onTertiaryContainerColor"),
    _SchemeKeyMap("error", "error"),
    _SchemeKeyMap("onError", "onErrorColor"),
    _SchemeKeyMap("errorContainer", "errorContainer"),
    _SchemeKeyMap("onErrorContainer", "onErrorContainerColor"),
    _SchemeKeyMap("background", "background"),
    _SchemeKeyMap("onBackground", "onBackgroundColor"),
    _SchemeKeyMap("surface", "surface"),
    _SchemeKeyMap("onSurface", "onSurfaceColor"),
    _SchemeKeyMap("surfaceVariant", "surfaceVariant"),
    _SchemeKeyMap("onSurfaceVariant", "onSurfaceVariantColor"),
    _SchemeKeyMap("outline", "outline"),
    _SchemeKeyMap("outlineVariant", "outlineVariant"),
    _SchemeKeyMap("shadow", "shadow"),
    _SchemeKeyMap("scrim", "scrim"),
    _SchemeKeyMap("inverseSurface", "inverseSurface"),
    _SchemeKeyMap("inverseOnSurface", "inverseOnSurface"),
    _SchemeKeyMap("inversePrimary", "inversePrimary"),
    _SchemeKeyMap("surfaceDim", "surfaceDim"),
    _SchemeKeyMap("surfaceBright", "surfaceBright"),
    _SchemeKeyMap("surfaceContainerLowest", "surfaceContainerLowest"),
    _SchemeKeyMap("surfaceContainerLow", "surfaceContainerLow"),
    _SchemeKeyMap("surfaceContainer", "surfaceContainer"),
    _SchemeKeyMap("surfaceContainerHigh", "surfaceContainerHigh"),
    _SchemeKeyMap("surfaceContainerHighest", "surfaceContainerHighest"),
)


def _argb_to_qcolor_hex(argb: int) -> str:
    return QColor.fromRgba(int(argb) & 0xFFFFFFFF).name(QColor.NameFormat.HexRgb).lower()


def _hex_to_qml_hex_rgb(hex_str: str) -> str:
    s = hex_str.strip().lower()
    if not s.startswith("#"):
        return s
    if len(s) == 9:
        return s[:7]
    return s


def _qcolor_to_argb(color: QColor) -> int:
    return int(color.rgba()) & 0xFFFFFFFF


def _url_to_local_path(file_url: QUrl) -> Optional[Path]:
    if file_url.isEmpty():
        return None
    if file_url.isLocalFile():
        local = file_url.toLocalFile()
        return Path(local) if local else None
    url_str = file_url.toString()
    if url_str.startswith("file:///"):
        return Path(url_str.replace("file:///", ""))
    return None


class StyleManager(QObject):
    isDarkThemeChanged = Signal()
    seedColorChanged = Signal()
    currentSchemeChanged = Signal()
    lightSchemeChanged = Signal()
    darkSchemeChanged = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._is_dark_theme: bool = False
        self._seed_color: QColor = QColor("#6750a4")
        self._current_scheme: dict[str, Any] = {}
        self._light_scheme: dict[str, Any] = {}
        self._dark_scheme: dict[str, Any] = {}

        app = QGuiApplication.instance()
        if app is not None:
            style_hints = app.styleHints()
            if style_hints is not None and hasattr(style_hints, "colorScheme"):
                try:
                    self._is_dark_theme = style_hints.colorScheme() == Qt.ColorScheme.Dark
                except Exception:
                    try:
                        self._is_dark_theme = style_hints.colorScheme() == 1
                    except Exception:
                        self._is_dark_theme = False

                if hasattr(style_hints, "colorSchemeChanged"):
                    try:
                        style_hints.colorSchemeChanged.connect(self._on_system_color_scheme_changed)
                    except Exception:
                        pass

        self._update_scheme()

    def _on_system_color_scheme_changed(self, scheme: Any) -> None:
        try:
            is_dark = bool(scheme == Qt.ColorScheme.Dark)
        except Exception:
            is_dark = bool(int(scheme) == 1) if scheme is not None else False
        self.setIsDarkTheme(is_dark)

    def getIsDarkTheme(self) -> bool:
        return self._is_dark_theme

    def setIsDarkTheme(self, is_dark: bool) -> None:
        is_dark = bool(is_dark)
        if self._is_dark_theme == is_dark:
            return
        self._is_dark_theme = is_dark
        self.isDarkThemeChanged.emit()
        self._update_scheme()

    def getSeedColor(self) -> QColor:
        return QColor(self._seed_color)

    def setSeedColor(self, color: QColor) -> None:
        if self._seed_color == color:
            return
        self._seed_color = QColor(color)
        self.seedColorChanged.emit()
        self._update_scheme()

    def getHctHue(self) -> float:
        try:
            from materialyoucolor.hct import Hct  # type: ignore

            hct = Hct.from_int(_qcolor_to_argb(self._seed_color))
            return float(getattr(hct, "hue", getattr(hct, "get_hue")()))
        except Exception:
            return 0.0

    def getHctChroma(self) -> float:
        try:
            from materialyoucolor.hct import Hct  # type: ignore

            hct = Hct.from_int(_qcolor_to_argb(self._seed_color))
            return float(getattr(hct, "chroma", getattr(hct, "get_chroma")()))
        except Exception:
            return 0.0

    def getHctTone(self) -> float:
        try:
            from materialyoucolor.hct import Hct  # type: ignore

            hct = Hct.from_int(_qcolor_to_argb(self._seed_color))
            return float(getattr(hct, "tone", getattr(hct, "get_tone")()))
        except Exception:
            return 0.0

    def getCurrentScheme(self) -> dict[str, Any]:
        return dict(self._current_scheme)

    def getLightScheme(self) -> dict[str, Any]:
        return dict(self._light_scheme)

    def getDarkScheme(self) -> dict[str, Any]:
        return dict(self._dark_scheme)

    @Slot(float, float, float)
    def setSeedColorHct(self, hue: float, chroma: float, tone: float) -> None:
        try:
            from materialyoucolor.hct import Hct  # type: ignore

            if hasattr(Hct, "from_hct"):
                hct = Hct.from_hct(float(hue), float(chroma), float(tone))
            else:
                hct = Hct(float(hue), float(chroma), float(tone))

            if hasattr(hct, "to_int"):
                argb = int(hct.to_int())
            else:
                argb = int(getattr(hct, "argb"))

            self.setSeedColor(QColor.fromRgba(argb))
        except Exception:
            return

    @Slot(QUrl)
    def setSourceImage(self, file_url: QUrl) -> None:
        local_path = _url_to_local_path(file_url)
        if local_path is None:
            return
        if not local_path.exists():
            return

        try:
            from materialyoucolor.quantize import ImageQuantizeCelebi  # type: ignore
            from materialyoucolor.score.score import Score  # type: ignore

            result = ImageQuantizeCelebi(str(local_path), 5, 128)
            ranked = Score.score(result)
            if ranked:
                self.setSeedColor(QColor.fromRgba(int(ranked[0]) & 0xFFFFFFFF))
                return
        except Exception:
            pass

        image = QImage(str(local_path))
        if image.isNull():
            return
        if image.width() > 128 or image.height() > 128:
            image = image.scaled(128, 128)
        image = image.convertToFormat(QImage.Format.Format_ARGB32)

        best = self._extract_dominant_color_simple(image)
        if best is not None:
            self.setSeedColor(QColor.fromRgba(best))

    def _update_scheme(self) -> None:
        argb = _qcolor_to_argb(self._seed_color)
        self._light_scheme = self._generate_scheme(argb, is_dark=False)
        self._dark_scheme = self._generate_scheme(argb, is_dark=True)
        self._current_scheme = self._dark_scheme if self._is_dark_theme else self._light_scheme

        self.lightSchemeChanged.emit()
        self.darkSchemeChanged.emit()
        self.currentSchemeChanged.emit()

    def _generate_scheme(self, argb: int, is_dark: bool) -> dict[str, Any]:
        try:
            from materialyoucolor.hct import Hct  # type: ignore
            from materialyoucolor.dynamiccolor.material_dynamic_colors import (  # type: ignore
                MaterialDynamicColors,
            )
            from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot  # type: ignore

            source = Hct.from_int(int(argb) & 0xFFFFFFFF)
            try:
                scheme = SchemeTonalSpot(source, bool(is_dark), 0.0, spec_version="2025")
                mdc = MaterialDynamicColors(spec="2025")
            except TypeError:
                scheme = SchemeTonalSpot(source, bool(is_dark), 0.0)
                mdc = MaterialDynamicColors()

            out: dict[str, Any] = {}
            for mapping in _SCHEME_KEYS:
                token = mapping.token
                qml_key = mapping.qml_key
                dyn = getattr(mdc, token)
                hex_rrggbbaa = str(dyn.get_hex(scheme))
                out[qml_key] = _hex_to_qml_hex_rgb(hex_rrggbbaa)
            return out
        except Exception:
            return self._generate_scheme_fallback(argb, is_dark=is_dark)

    def _generate_scheme_fallback(self, argb: int, is_dark: bool) -> dict[str, Any]:
        base = QColor.fromRgba(int(argb) & 0xFFFFFFFF)
        if is_dark:
            background = QColor("#121212")
            surface = QColor("#1a1a1a")
            on_surface = QColor("#ffffff")
        else:
            background = QColor("#ffffff")
            surface = QColor("#fdf7ff")
            on_surface = QColor("#1c1b1f")

        out: dict[str, Any] = {
            "primary": _argb_to_qcolor_hex(base.rgba()),
            "onPrimaryColor": _argb_to_qcolor_hex(QColor("#ffffff").rgba()),
            "primaryContainer": _argb_to_qcolor_hex(base.lighter(160).rgba()),
            "onPrimaryContainerColor": _argb_to_qcolor_hex(QColor("#000000").rgba()),
            "secondary": _argb_to_qcolor_hex(base.darker(120).rgba()),
            "onSecondaryColor": _argb_to_qcolor_hex(QColor("#ffffff").rgba()),
            "secondaryContainer": _argb_to_qcolor_hex(base.lighter(140).rgba()),
            "onSecondaryContainerColor": _argb_to_qcolor_hex(QColor("#000000").rgba()),
            "tertiary": _argb_to_qcolor_hex(base.darker(140).rgba()),
            "onTertiaryColor": _argb_to_qcolor_hex(QColor("#ffffff").rgba()),
            "tertiaryContainer": _argb_to_qcolor_hex(base.lighter(150).rgba()),
            "onTertiaryContainerColor": _argb_to_qcolor_hex(QColor("#000000").rgba()),
            "error": _argb_to_qcolor_hex(QColor("#b3261e").rgba()),
            "onErrorColor": _argb_to_qcolor_hex(QColor("#ffffff").rgba()),
            "errorContainer": _argb_to_qcolor_hex(QColor("#f9dedc").rgba()),
            "onErrorContainerColor": _argb_to_qcolor_hex(QColor("#410e0b").rgba()),
            "background": _argb_to_qcolor_hex(background.rgba()),
            "onBackgroundColor": _argb_to_qcolor_hex(on_surface.rgba()),
            "surface": _argb_to_qcolor_hex(surface.rgba()),
            "onSurfaceColor": _argb_to_qcolor_hex(on_surface.rgba()),
            "surfaceVariant": _argb_to_qcolor_hex(surface.darker(110).rgba()),
            "onSurfaceVariantColor": _argb_to_qcolor_hex(on_surface.lighter(120).rgba()),
            "outline": _argb_to_qcolor_hex(QColor("#79747e").rgba()),
            "outlineVariant": _argb_to_qcolor_hex(QColor("#cac4d0").rgba()),
            "shadow": _argb_to_qcolor_hex(QColor("#000000").rgba()),
            "scrim": _argb_to_qcolor_hex(QColor("#000000").rgba()),
            "inverseSurface": _argb_to_qcolor_hex(QColor("#313033").rgba()),
            "inverseOnSurface": _argb_to_qcolor_hex(QColor("#f4eff4").rgba()),
            "inversePrimary": _argb_to_qcolor_hex(base.lighter(170).rgba()),
            "surfaceDim": _argb_to_qcolor_hex(surface.darker(120).rgba()),
            "surfaceBright": _argb_to_qcolor_hex(surface.lighter(110).rgba()),
            "surfaceContainerLowest": _argb_to_qcolor_hex(background.rgba()),
            "surfaceContainerLow": _argb_to_qcolor_hex(surface.lighter(102).rgba()),
            "surfaceContainer": _argb_to_qcolor_hex(surface.lighter(104).rgba()),
            "surfaceContainerHigh": _argb_to_qcolor_hex(surface.lighter(106).rgba()),
            "surfaceContainerHighest": _argb_to_qcolor_hex(surface.lighter(108).rgba()),
        }
        return out

    def _extract_dominant_color_simple(self, image: QImage) -> Optional[int]:
        w = image.width()
        h = image.height()
        if w <= 0 or h <= 0:
            return None

        counts: dict[int, int] = {}
        for y in range(h):
            for x in range(w):
                rgba = int(image.pixel(x, y)) & 0xFFFFFFFF
                a = (rgba >> 24) & 0xFF
                if a < 128:
                    continue
                r = (rgba >> 16) & 0xFF
                g = (rgba >> 8) & 0xFF
                b = rgba & 0xFF

                mx = max(r, g, b)
                mn = min(r, g, b)
                if (mx - mn) < 10:
                    continue

                key = ((r >> 3) << 10) | ((g >> 3) << 5) | (b >> 3)
                counts[key] = counts.get(key, 0) + 1

        if not counts:
            return None

        best_key = max(counts, key=counts.get)
        r5 = (best_key >> 10) & 0x1F
        g5 = (best_key >> 5) & 0x1F
        b5 = best_key & 0x1F
        r = (r5 << 3) | (r5 >> 2)
        g = (g5 << 3) | (g5 >> 2)
        b = (b5 << 3) | (b5 >> 2)
        return (0xFF << 24) | (r << 16) | (g << 8) | b

    isDarkTheme = Property(bool, getIsDarkTheme, setIsDarkTheme, notify=isDarkThemeChanged)
    seedColor = Property(QColor, getSeedColor, setSeedColor, notify=seedColorChanged)
    hctHue = Property(float, getHctHue, notify=seedColorChanged)
    hctChroma = Property(float, getHctChroma, notify=seedColorChanged)
    hctTone = Property(float, getHctTone, notify=seedColorChanged)
    currentScheme = Property("QVariantMap", getCurrentScheme, notify=currentSchemeChanged)
    lightScheme = Property("QVariantMap", getLightScheme, notify=lightSchemeChanged)
    darkScheme = Property("QVariantMap", getDarkScheme, notify=darkSchemeChanged)
