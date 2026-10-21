<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="Aryan Deshmukh, full stack developer with a backend focus, Pune" src="assets/banner-light.svg" width="100%">
</picture>

<br>

[**Portfolio**](https://a-ryan-1.github.io/Portfolio-Website/) &nbsp;|&nbsp; [**LinkedIn**](https://www.linkedin.com/in/aryan-deshmukh-793840259/) &nbsp;|&nbsp; [**Medium**](https://medium.com/@aryan0deshmukh) &nbsp;|&nbsp; [**LeetCode**](https://leetcode.com/u/DarKKKKKnight/)

</div>

## About

I am a full stack developer with a backend focus at Josh Software in Pune, working on a production IoT water-metering and utility-billing platform. Meter readings arrive over MQTT into a Go service, a Ruby on Rails API turns them into bills, and React apps serve admins and residents, all on AWS. I own the billing module and built site onboarding end to end. My best stories come from production debugging, so I write them up.

Joined as an intern in January 2026 and converted to full-time in six months. B.Tech in Computer Engineering (Honours in Cyber Security), CGPA 9.26.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/numbers-dark.svg">
  <img alt="30+ pull requests shipped, 11 open-source PRs merged, 660 LeetCode problems solved, 3 engineering posts" src="assets/numbers-light.svg" width="100%">
</picture>

## What I work with

| | |
|---|---|
| **Languages** | ![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white) ![Ruby](https://img.shields.io/badge/Ruby-CC342D?style=flat-square&logo=ruby&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) ![C++](https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white) |
| **Backend** | ![Rails](https://img.shields.io/badge/Rails-D30001?style=flat-square&logo=rubyonrails&logoColor=white) ![Gin](https://img.shields.io/badge/Gin-008ECF?style=flat-square&logo=gin&logoColor=white) ![Sidekiq](https://img.shields.io/badge/Sidekiq-B1003E?style=flat-square&logoColor=white) ![MQTT](https://img.shields.io/badge/MQTT-660066?style=flat-square&logo=mqtt&logoColor=white) |
| **Frontend** | ![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB) ![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white) |
| **Data and cloud** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) |

## Selected fixes

Upstream fixes, each reproduced before claiming it, with the evidence in the PR.

### Kepler: the Helm chart now runs unprivileged by default

- Failure: the chart ran the exporter as `privileged: true`, which many clusters refuse.
- Fix: showed on a kind cluster that `SYS_PTRACE` alone is enough and made it the default, with `privileged: true` one value away; upgrades, AppArmor, SELinux and GPU nodes handled.
- Result: 587 metric lines unprivileged against 604 privileged. Review found 0 container and 0 pod series on cgroupfs nodes; the second PR restored them (72 and 36) and a CI check in the third guards them. [PR #2584](https://github.com/sustainable-computing-io/kepler/pull/2584), [#2591](https://github.com/sustainable-computing-io/kepler/pull/2591), [#2592](https://github.com/sustainable-computing-io/kepler/pull/2592)

### Prometheus Operator: bad AlertmanagerConfig and ScrapeConfig input caught early

- Failure: the operator accepted duplicate time intervals and credential-less Webex receivers that Alertmanager then refused, and its Azure discovery silently dropped settings.
- Fix: validation for both API versions, and the missing Azure fields written with the generator's own helpers.
- Result: every change pinned by tests that fail without it, including a golden-file case combining environment, authorization, proxy and redirects. [PR #8896](https://github.com/prometheus-operator/prometheus-operator/pull/8896), [#8897](https://github.com/prometheus-operator/prometheus-operator/pull/8897), [#8898](https://github.com/prometheus-operator/prometheus-operator/pull/8898)

### CopyQ: a frameless window and a hidden menu bar

- Failure: users wanted a compact clipboard manager; the frameless option existed in code with no way to turn it on.
- Fix: proved dragging and resizing work on Wayland with a throwaway Qt window first, then built the checkbox, resize grip and drag-from-body; the menu bar collapses to zero height so its shortcuts still work.
- Result: eight review rounds across two PRs, both merged. [PR #3733](https://github.com/hluk/CopyQ/pull/3733), [#3732](https://github.com/hluk/CopyQ/pull/3732)

## Contributions

<p align="center">
  <a href="https://github.com/sustainable-computing-io/kepler"><img src="https://github.com/sustainable-computing-io.png?size=64" width="48" height="48" alt="Kepler" title="Kepler"></a>
  <a href="https://github.com/prometheus-operator/prometheus-operator"><img src="https://github.com/prometheus-operator.png?size=64" width="48" height="48" alt="Prometheus Operator" title="Prometheus Operator"></a>
  <a href="https://github.com/hluk/CopyQ"><img src="https://github.com/hluk.png?size=64" width="48" height="48" alt="CopyQ" title="CopyQ"></a>
  <a href="https://github.com/ONEARMY/community-platform"><img src="https://github.com/ONEARMY.png?size=64" width="48" height="48" alt="ONEARMY community-platform" title="ONEARMY community-platform"></a>
</p>

<!-- contrib:start -->
| Project | What it is | Merged PRs | Stars |
|---|---|---|---|
| [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) | Kubernetes operator for Prometheus and Alertmanager | 3 | ![stars](https://img.shields.io/github/stars/prometheus-operator/prometheus-operator?style=flat-square&logo=github&color=lightgrey) |
| [Kepler](https://github.com/sustainable-computing-io/kepler) | Energy use per Kubernetes pod and container, as Prometheus metrics | 3 | ![stars](https://img.shields.io/github/stars/sustainable-computing-io/kepler?style=flat-square&logo=github&color=lightgrey) |
| [community-platform](https://github.com/ONEARMY/community-platform) | Precious Plastic community platform (React, TypeScript) | 3 | ![stars](https://img.shields.io/github/stars/ONEARMY/community-platform?style=flat-square&logo=github&color=lightgrey) |
| [CopyQ](https://github.com/hluk/CopyQ) | Clipboard manager with advanced features (C++, Qt) | 2 | ![stars](https://img.shields.io/github/stars/hluk/CopyQ?style=flat-square&logo=github&color=lightgrey) |
<!-- contrib:end -->

Open now: [cert-manager](https://github.com/cert-manager/cert-manager), [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator), [Rook](https://github.com/rook/rook) and [Argo Rollouts](https://github.com/argoproj/argo-rollouts). GitHub lists them under "Contributed to" on this profile.

## Writing

Production bugs, written as stories with the measured fix.

- [The Water That Flowed Backwards](https://medium.com/@aryan0deshmukh/the-water-that-flowed-backwards-2a7d6bb04c7c): one line of Go made meters report negative consumption.
- [The Restart Command That Only Worked When a Human Typed It](https://medium.com/@aryan0deshmukh/the-restart-command-that-only-worked-when-a-human-typed-it-941d30319d22): the command was right; the shell was not.
- [The Fix That Only Reached Half the Server](https://medium.com/@aryan0deshmukh/the-fix-that-only-reached-half-the-server-942aeb0665ac): one feature recovered after a config fix while the other failed for a day and a half.

## Get in touch

I am happy to talk about backend systems, IoT data pipelines and open source. The fastest way is [LinkedIn](https://www.linkedin.com/in/aryan-deshmukh-793840259/).
