### Rook: encrypted object stores can use a Vault transit engine mounted anywhere

- Failure: Rook always sent SSE-S3 requests to `/v1/transit`, so a Vault transit engine mounted at another path failed with `Request to Vault failed with error -13`.
- Fix: my first version honoured the existing `VAULT_BACKEND_PATH`; against a real RGW and Vault I reproduced the reviewer's warning that it would break stores whose examples already set that key. I switched to a new opt-in `VAULT_TRANSIT_BACKEND_PATH`, so existing stores render the same flags as before.
- Result: five real-RGW runs covering the old behaviour, the break, the final design and the original bug, plus a seven-case unit test that checks both the token and Vault Agent flags. Merged in 15 days.
