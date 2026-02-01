# winMsg.py Overview

`winMsg.py` is a Tkinter-based utility that opens a tabbed window and runs configured shell commands after a short delay, showing each command's stdout/stderr inside its tab.

## Configuration (winMsg.ini)

- Create matching `labelN` / `cN` pairs (same suffix) to define a tab title and the shell command to execute inside it.
- Optional `sleep`, `delay`, `sleep_seconds`, or `wait` entries set the one-time startup delay (seconds, default 3) before any command runs.
- Optional `delayN` entries (matching the label/command suffix) set per-command delays in seconds; they default to 1 second if omitted.
- Lines starting with `#` or `;`, blank lines, and keys without `=` are ignored. Unpaired labels/commands are skipped.

## Runtime behavior

1. The window is sized to roughly 60% of the screen and centered.
2. Each label/command pair gets a tab with a read-only text widget that shows the command and its scheduled per-command delay.
3. Once the global delay elapses, commands are sorted by their `delayN` values, distributed round-robin across three worker threads, and each thread sleeps only as long as needed to satisfy the next task's delay budget before running it.
4. When a command finishes, its tab is updated with the captured stdout, stderr, and exit code, and the text area remains read-only.

## Fallback mode

If no valid label/command pairs exist, the app shows a single tab (labeled from `argv[1]` or "Info") explaining how to populate `winMsg.ini` so commands can be displayed.

## Scheduling details

- After parsing, tasks are sorted by their per-command delay (default 1s) to ensure shorter waits run first.
- Tasks are assigned round-robin to three worker threads using their order in the sorted list (task index modulo 3); threads with no assigned work simply idle.
- Each worker keeps track of how many seconds it has already slept and waits only the additional time needed to reach the next task's target delay, so command runtime never counts toward future delays.
