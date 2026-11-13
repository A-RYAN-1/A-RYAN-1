### rclone: the mount's background downloader limits are now flags

- Failure: streaming audio from a mount with `--vfs-cache-mode full` stopped and restarted its download thread every few seconds, because a 5 second idle limit and a 10 error limit were hard-coded in the downloader (issue #10148); a broken backend could also freeze a mount for minutes.
- Fix: two documented flags, `--vfs-cache-downloader-idle-time` and `--vfs-cache-downloader-max-errors`, carried through the existing VFS options struct, with defaults equal to the old constants so nothing changes unless set. The maintainer asked for the family's flag prefix, so I renamed them.
- Result: two timer-based tests (50 ms limit, `assert.Eventually`), merged in 21 days after one naming round and one approval.
