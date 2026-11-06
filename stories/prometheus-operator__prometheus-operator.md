### Prometheus Operator: bad AlertmanagerConfig and ScrapeConfig input caught early

- Failure: the operator accepted duplicate time intervals and credential-less Webex receivers that Alertmanager then refused, and its Azure discovery silently dropped settings.
- Fix: validation for both API versions, and the missing Azure fields written with the generator's own helpers.
- Result: every change pinned by tests that fail without it, including a golden-file case combining environment, authorization, proxy and redirects.
