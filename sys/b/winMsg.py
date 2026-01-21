#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple

CONFIG_PATH = Path(__file__).with_name("winMsg.ini")
DEFAULT_DELAY_SECONDS = 3.0


@dataclass
class TabInfo:
    label: str
    command: str
    text_widget: tk.Text


def configure_window(root: tk.Tk) -> None:
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    width = int(screen_w * 0.6)
    height = int(screen_h * 0.6)
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def _extract_delay(value: str) -> float | None:
    tokens = value.replace(",", " ").split()
    for token in tokens:
        try:
            seconds = float(token)
        except ValueError:
            continue
        if seconds >= 0:
            return seconds
    return None


def parse_config(path: Path) -> Tuple[List[Tuple[str, str]], float]:
    labels: dict[str, str] = {}
    commands: dict[str, str] = {}
    delay_seconds = DEFAULT_DELAY_SECONDS

    if not path.exists():
        return [], delay_seconds

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        normalized_key = key.strip().lower()
        value = value.strip()
        if normalized_key.startswith("label"):
            idx = normalized_key[5:]
            labels[idx] = value
        elif normalized_key.startswith("c"):
            idx = normalized_key[1:]
            commands[idx] = value
        elif normalized_key in {"sleep", "delay", "sleep_seconds", "wait"}:
            parsed = _extract_delay(value)
            if parsed is not None:
                delay_seconds = parsed

    def sort_key(token: str) -> Tuple[int, object]:
        return (0, int(token)) if token.isdigit() else (1, token)

    entries: List[Tuple[str, str]] = []
    for idx in sorted(labels.keys(), key=sort_key):
        if idx in commands:
            entries.append((labels[idx], commands[idx]))

    return entries, delay_seconds


def run_command(command: str) -> str:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover
        return f"Command:\n{command}\n\nError executing command:\n{exc}"

    parts: List[str] = []
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        parts.append(stdout)
    if stderr:
        parts.append("STDERR:\n" + stderr)

    body = "\n\n".join(parts) if parts else "<no output>"
    return (
        f"Command:\n{command}\n\n"
        f"Exit code: {completed.returncode}\n\n"
        f"{body}"
    )


def update_text_widget(widget: tk.Text, text: str) -> None:
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", text)
    widget.configure(state="disabled")


def build_command_tabs(root: tk.Tk, entries: List[Tuple[str, str]], delay_seconds: float) -> List[TabInfo]:
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_infos: List[TabInfo] = []
    wait_message = (
        "Waiting to run command...\n"
        f"(Execution starts {delay_seconds:g} seconds after window opens.)"
    )

    for label_text, command in entries:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=label_text)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_widget = tk.Text(frame, wrap="word", font=("Segoe UI", 12))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        placeholder = f"Command:\n{command}\n\n{wait_message}"
        update_text_widget(text_widget, placeholder)

        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tab_infos.append(TabInfo(label_text, command, text_widget))

    return tab_infos


def build_fallback_tab(root: tk.Tk, title: str, message: str) -> None:
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    frame = ttk.Frame(notebook)
    notebook.add(frame, text=title)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    text_widget = tk.Text(frame, wrap="word", font=("Segoe UI", 12))
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    update_text_widget(text_widget, message)

    text_widget.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")


def start_background_execution(root: tk.Tk, tab_infos: List[TabInfo], delay_seconds: float) -> None:
    def worker() -> None:
        time.sleep(delay_seconds)
        for info in tab_infos:
            output = run_command(info.command)
            root.after(0, update_text_widget, info.text_widget, output)

    Thread(target=worker, daemon=True).start()


def main() -> None:
    root = tk.Tk()
    root.title("winMsg")
    configure_window(root)

    entries, delay_seconds = parse_config(CONFIG_PATH)
    if entries:
        tab_infos = build_command_tabs(root, entries, delay_seconds)
        start_background_execution(root, tab_infos, delay_seconds)
    else:
        fallback_label = sys.argv[1] if len(sys.argv) > 1 else "Info"
        message = (
            f"No label/command pairs found in {CONFIG_PATH}.\n"
            "Add entries like:\n\n"
            "label1=My Task\n"
            "c1=/path/to/script\n"
            "sleep=3"
        )
        build_fallback_tab(root, fallback_label, message)

    root.mainloop()


if __name__ == "__main__":
    main()
