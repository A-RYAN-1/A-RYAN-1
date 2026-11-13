### TiDB: SOUNDEX() now exists, matching MySQL byte for byte

- Failure: `SELECT SOUNDEX(name)` failed with "FUNCTION soundex does not exist" (issue #3930, open since 2017), so a MySQL migration with SOUNDEX in a query broke outright. An earlier attempt had been closed unmerged.
- Fix: one encoder with three modes (UTF-8 characters, Latin-1 bytes, binary) chosen once when the signature is built, scalar and vectorized. A reviewer caught my first Latin-1 rule as a mismatch, so I read MySQL's own character table and tested all 256 leading bytes against a real MySQL 8.0.46.
- Result: merged in 19 days with two approvals, 12 files; the reviewer re-ran 65,792 Latin-1 cases himself, and a maintainer wrote the companion test PR.
