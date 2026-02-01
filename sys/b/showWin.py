#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import cycle
from pathlib import Path

import gi

# Ensure GTK dependencies are discovered before importing the rest of gi.repository.
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GLib, Gio, Gtk, GdkPixbuf

GLib.set_prgname("showWin")
GLib.set_application_name("showWin")

WINDOW_SIZE = (100, 40)
ICON_PATHS = [
    Path("/b/res/red.png"),
    Path("/b/res/blue.png"),
]
PULSE_INTERVAL_MS = 1000


@dataclass(frozen=True)
class IconAsset:
    pixbuf: GdkPixbuf.Pixbuf
    path: Path | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show a small alert window with dynamic text.")
    parser.add_argument("message", help="Text to display inside the window")
    return parser


def _solid_pixbuf(color: str, size: int = 64) -> GdkPixbuf.Pixbuf:
    color = color.lstrip("#")
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    pixel = bytes((r, g, b, 255))
    buffer = pixel * (size * size)
    return GdkPixbuf.Pixbuf.new_from_bytes(
        GLib.Bytes.new(buffer),
        GdkPixbuf.Colorspace.RGB,
        True,
        8,
        size,
        size,
        size * 4,
    )


def load_icons() -> list[IconAsset]:
    icons: list[IconAsset] = []
    for path in ICON_PATHS:
        if not path.is_file():
            continue
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path))
        except GLib.Error as exc:
            print(f"Error loading icon {path}: {exc}")
        else:
            icons.append(IconAsset(pixbuf=pixbuf, path=path))
    if not icons:
        icons = [
            IconAsset(_solid_pixbuf("#ff3b30")),
            IconAsset(_solid_pixbuf("#007bff")),
        ]
    return icons


class ShowWinApp(Gtk.Application):
    def __init__(self, message: str) -> None:
        super().__init__(application_id="com.example.showwin", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.message = message
        self.icons = load_icons()
        self.icon_cycle = cycle(self.icons)

    def do_activate(self) -> None:  # type: ignore[override]
        window = self.props.active_window
        if window is None:
            window = self._build_window()
        window.present()

    def _build_window(self) -> Gtk.ApplicationWindow:
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("showWin")
        window.set_default_size(*WINDOW_SIZE)
        window.set_resizable(False)
        window.set_wmclass("showWin", "showWin")

        label = Gtk.Label(label=self.message)
        label.set_line_wrap(True)
        label.set_justify(Gtk.Justification.CENTER)
        window.add(label)

        Gtk.Window.set_default_icon_list([asset.pixbuf for asset in self.icons])
        window.connect("realize", self._on_window_realize)
        window.show_all()
        return window

    def _on_window_realize(self, window: Gtk.Window) -> None:
        self._apply_icon(window, next(self.icon_cycle))
        GLib.timeout_add(PULSE_INTERVAL_MS, self._pulse_icon, window)
        GLib.idle_add(self._bring_to_front, window)

    def _apply_icon(self, window: Gtk.Window, asset: IconAsset) -> None:
        if asset.path and asset.path.is_file():
            try:
                window.set_icon_from_file(str(asset.path))
            except GLib.Error as exc:
                print(f"Error applying icon {asset.path}: {exc}")
                window.set_icon(asset.pixbuf)
        else:
            window.set_icon(asset.pixbuf)
        Gtk.Window.set_default_icon_list([asset.pixbuf])

    def _pulse_icon(self, window: Gtk.Window) -> bool:
        self._apply_icon(window, next(self.icon_cycle))
        return True

    def _bring_to_front(self, window: Gtk.Window) -> bool:
        window.present()
        window.set_keep_above(True)
        GLib.timeout_add(1500, self._release_keep_above, window)
        return False

    def _release_keep_above(self, window: Gtk.Window) -> bool:
        window.set_keep_above(False)
        return False


def main() -> None:
    args = build_parser().parse_args()
    app = ShowWinApp(args.message)
    app.run([])


if __name__ == "__main__":
    main()
