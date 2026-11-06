### CopyQ: a frameless window and a hidden menu bar

- Failure: users wanted a compact clipboard manager; the frameless option existed in code with no way to turn it on.
- Fix: proved dragging and resizing work on Wayland with a throwaway Qt window first, then built the checkbox, resize grip and drag-from-body; the menu bar collapses to zero height so its shortcuts still work.
- Result: eight review rounds across two PRs, both merged.
- Reuse: the menu bar commit is indexed in the [XERJ Corpus Hub](https://hub.xerj.org/contributors/A-RYAN-1) as a worked reference for AI coding agents, under CopyQ's GPL-3.0 licence with attribution.
