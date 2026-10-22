#!/usr/bin/env python3
"""Refresh the live parts of the profile: assets/numbers-*.svg, assets/leetcode-*.svg,
assets/activity-*.svg and the generated blocks of README.md (numbers alt text, contributions table).
Standard library only. Needs GITHUB_TOKEN or GH_TOKEN (or `gh auth token`) for GitHub; LeetCode is public.
Run by .github/workflows/update-profile.yml every day, or by hand from the repo root."""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ME = "A-RYAN-1"
LEETCODE = "DarKKKKKnight"
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
SKIP_OWNERS = {ME.lower(), "biagiopietro"}
WHAT = {
    "sustainable-computing-io/kepler": ("Kepler", "Energy use per Kubernetes pod and container, as Prometheus metrics"),
    "prometheus-operator/prometheus-operator": ("Prometheus Operator", "Kubernetes operator for Prometheus and Alertmanager"),
    "hluk/CopyQ": ("CopyQ", "Clipboard manager with advanced features (C++, Qt)"),
    "ONEARMY/community-platform": ("community-platform", "Precious Plastic community platform (React, TypeScript)"),
}
THEMES = {
    "light": dict(bg1="#f6f8fa", bg2="#e6edf7", ink="#0d1117", mut="#57606a", acc="#0969da", acc2="#8250df", card="#ffffff", line="#d0d7de",
                  lv=["#ebedf0", "#b6d4fb", "#6aa7f0", "#2f7fe0", "#0a4fa8"], easy="#1a7f37", medium="#bf8700", hard="#cf222e"),
    "dark": dict(bg1="#0d1117", bg2="#161b22", ink="#f0f6fc", mut="#8b949e", acc="#58a6ff", acc2="#bc8cff", card="#161b22", line="#30363d",
                 lv=["#21262d", "#12335f", "#1f5fae", "#388bfd", "#79c0ff"], easy="#3fb950", medium="#d29922", hard="#f85149"),
}
F = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    env = {**os.environ, "GH_CONFIG_DIR": str(Path.home() / ".config" / "gh-aryan1")}
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True, env=env).stdout.strip()


def http(url, body=None, headers=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"User-Agent": "profile-updater", **(headers or {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429) or attempt == 3:
                raise
            time.sleep(60 * (attempt + 1))


def gh_get(path, tok):
    return http("https://api.github.com" + path, headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})


def gh_graphql(query, tok, variables=None):
    d = http("https://api.github.com/graphql", {"query": query, "variables": variables or {}}, {"Authorization": f"Bearer {tok}"})
    if "errors" in d:
        raise RuntimeError(d["errors"])
    return d["data"]


def leetcode():
    q = "query($u:String!){matchedUser(username:$u){submitStatsGlobal{acSubmissionNum{difficulty count}} profile{ranking}}}"
    d = http("https://leetcode.com/graphql", {"query": q, "variables": {"u": LEETCODE}},
             {"Content-Type": "application/json", "Referer": "https://leetcode.com"})["data"]["matchedUser"]
    c = {x["difficulty"]: x["count"] for x in d["submitStatsGlobal"]["acSubmissionNum"]}
    return dict(total=c["All"], easy=c["Easy"], medium=c["Medium"], hard=c["Hard"], rank=d["profile"]["ranking"])


def merged_prs(tok):
    """{repo: [pr numbers]} for merged PRs of ours in other people's repos."""
    out = defaultdict(list)
    page = 1
    while True:
        d = gh_get(f"/search/issues?q=author:{ME}+is:pr+is:merged&per_page=100&page={page}", tok)
        for it in d["items"]:
            repo = it["repository_url"].split("/repos/")[1]
            if repo.split("/")[0].lower() not in SKIP_OWNERS:
                out[repo].append(it["number"])
        if len(d["items"]) < 100:
            break
        page += 1
    return {r: sorted(n) for r, n in out.items()}


def live_projects(tok):
    repos = gh_get(f"/users/{ME}/repos?per_page=100&type=owner", tok)
    return sum(1 for r in repos if not r["fork"] and r["name"] != ME and (r.get("homepage") or r.get("has_pages")))


def calendar(tok):
    q = "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}"
    c = gh_graphql(q, tok, {"u": ME})["user"]["contributionsCollection"]["contributionCalendar"]
    return c["totalContributions"], [[d["contributionCount"] for d in w["contributionDays"]] for w in c["weeks"]]


def grad(c):
    return (f'<defs><linearGradient id="a" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["acc"]}"/>'
            f'<stop offset="1" stop-color="{c["acc2"]}"/></linearGradient></defs>')


def numbers_svg(c, items):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="150" viewBox="0 0 1200 150" role="img" aria-label="Numbers">{grad(c)}'
    for i, (a, b, d) in enumerate(items):
        x = i * 300 + 6
        s += (f'<rect x="{x}" y="6" width="282" height="138" rx="12" fill="{c["card"]}" stroke="{c["line"]}"/>'
              f'<rect x="{x}" y="6" width="282" height="5" rx="2" fill="url(#a)"/>'
              f'<text x="{x+24}" y="68" {F} font-size="46" font-weight="800" fill="{c["ink"]}">{a}</text>'
              f'<text x="{x+24}" y="98" {F} font-size="17" font-weight="600" fill="{c["acc"]}">{b}</text>'
              f'<text x="{x+24}" y="122" {F} font-size="13" fill="{c["mut"]}">{d}</text>')
    return s + "</svg>"


def leetcode_svg(c, lc):
    x0, bw = 300, 860
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="150" viewBox="0 0 1200 150" role="img" '
         f'aria-label="LeetCode: {lc["total"]} solved, {lc["easy"]} easy, {lc["medium"]} medium, {lc["hard"]} hard">{grad(c)}'
         f'<rect x="6" y="6" width="1188" height="138" rx="12" fill="{c["card"]}" stroke="{c["line"]}"/>'
         f'<rect x="6" y="6" width="1188" height="5" rx="2" fill="url(#a)"/>'
         f'<text x="30" y="72" {F} font-size="50" font-weight="800" fill="{c["ink"]}">{lc["total"]}</text>'
         f'<text x="30" y="100" {F} font-size="17" font-weight="600" fill="{c["acc"]}">LeetCode solved</text>'
         f'<text x="30" y="124" {F} font-size="13" fill="{c["mut"]}">in C++, global rank {lc["rank"]:,}</text>')
    keys = (("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard"))
    s += f'<clipPath id="r"><rect x="{x0}" y="48" width="{bw}" height="16" rx="8"/></clipPath><g clip-path="url(#r)">'
    x = x0
    for key, _ in keys:
        seg = max(bw * lc[key] / lc["total"], 6)
        s += f'<rect x="{x:.1f}" y="48" width="{seg:.1f}" height="16" fill="{c[key]}"/>'
        x += seg
    s += "</g>"
    lx = x0
    for key, label in keys:
        s += (f'<circle cx="{lx+6}" cy="94" r="6" fill="{c[key]}"/>'
              f'<text x="{lx+20}" y="99" {F} font-size="15" font-weight="600" fill="{c["ink"]}">{lc[key]}</text>'
              f'<text x="{lx+20+len(str(lc[key]))*9+6}" y="99" {F} font-size="15" fill="{c["mut"]}">{label}</text>')
        lx += 190
    return s + "</svg>"


def activity_svg(c, total, weeks):
    gap, left, top, w = 5, 30, 62, 1200
    cell = (w - 2 * left - (len(weeks) - 1) * gap) / len(weeks)
    h = int(top + 7 * (cell + gap) + 12)
    peak = max((n for wk in weeks for n in wk), default=1) or 1
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
         f'aria-label="{total} contributions in the last year">'
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{c["card"]}" stroke="{c["line"]}"/>'
         f'<text x="{left}" y="38" {F} font-size="20" font-weight="700" fill="{c["ink"]}">{total:,} contributions in the last year</text>')
    for i, wk in enumerate(weeks):
        for j, n in enumerate(wk):
            lv = 0 if n == 0 else min(4, 1 + int(3 * (n - 1) / max(peak - 1, 1)))
            s += f'<rect x="{left + i*(cell+gap):.1f}" y="{top + j*(cell+gap):.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="3" fill="{c["lv"][lv]}"/>'
    return s + "</svg>"


def pr_table(prs):
    rows = ["| Project | What it is | Merged PRs | Stars |", "|---|---|---|---|"]
    for repo, nums in sorted(prs.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        name, desc = WHAT.get(repo, (repo.split("/")[1], "TODO: describe in WHAT"))
        links = " ".join(f"[#{n}](https://github.com/{repo}/pull/{n})" for n in nums)
        badge = f"![stars](https://img.shields.io/github/stars/{repo}?style=flat-square&logo=github&color=lightgrey)"
        rows.append(f"| [{name}](https://github.com/{repo}) | {desc} | {links} | {badge} |")
    return "\n".join(rows)


def replace_block(text, name, body):
    return re.sub(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", lambda m: m.group(1) + body + m.group(2), text, flags=re.S)


def main():
    tok = token()
    prs = merged_prs(tok)
    n_prs = sum(len(v) for v in prs.values())
    lc = leetcode()
    live = live_projects(tok)
    raw = README.read_bytes().decode("utf-8")
    text = raw.replace("\r\n", "\n")
    writing = text.split("## Writing", 1)[-1].split("## ", 1)[0]
    posts = len(set(re.findall(r"medium\.com/@aryan0deshmukh/[\w-]+", writing)))
    total, weeks = calendar(tok)
    items = [(str(n_prs), "open-source PRs merged", f"{len(prs)} projects, linked below"),
             (str(lc["total"]), "LeetCode problems", f'{lc["easy"]} easy, {lc["medium"]} medium, {lc["hard"]} hard'),
             (str(posts), "engineering posts", "on production debugging"),
             (str(live), "projects live", "deployed on free tiers")]
    ASSETS.mkdir(exist_ok=True)
    for n, c in THEMES.items():
        (ASSETS / f"numbers-{n}.svg").write_text(numbers_svg(c, items), encoding="utf-8")
        (ASSETS / f"leetcode-{n}.svg").write_text(leetcode_svg(c, lc), encoding="utf-8")
        (ASSETS / f"activity-{n}.svg").write_text(activity_svg(c, total, weeks), encoding="utf-8")
    alt = f"{n_prs} open-source PRs merged, {lc['total']} LeetCode problems solved, {posts} engineering posts, {live} projects live"
    text = re.sub(r'(<!-- numbers:start -->.*?<img alt=")[^"]*(")', lambda m: m.group(1) + alt + m.group(2), text, flags=re.S)
    text = replace_block(text, "contrib", pr_table(prs))
    new = text.replace("\n", "\r\n") if "\r\n" in raw else text
    if new != raw:
        README.write_bytes(new.encode("utf-8"))
    print(f"{n_prs} merged PRs in {len(prs)} repos; leetcode {lc['total']}; {live} live; {posts} posts; {total} contributions")


if __name__ == "__main__":
    main()
