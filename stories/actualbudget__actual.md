### Actual Budget: bank sync outages now say what happened

- Failure: when SimpleFIN returned a maintenance page, the sync banner showed "An internal error occurred". The server had since learned to answer `SERVER_DOWN`, but the client had no mapping for it.
- Fix: a new `server-down` sync status carried through the account model, the database type and the error mapping, with its own banner message. No migration was needed because the column is free text.
- Result: three tests, one per layer, that fail without the change and pass with it; typecheck clean.
