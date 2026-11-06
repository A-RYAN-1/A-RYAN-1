#!/usr/bin/env python3
"""Refresh the live parts of the profile: assets/numbers-*.svg, assets/leetcode-*.svg,
the generated blocks of README.md (numbers alt text, logo row, contributions table, open-PR line (links to the PRs), selected-fixes stories (stories/*.md, top 3 by stars),
XERJ Corpus Hub section,
writing list from the Medium feed).
Standard library only. Needs GITHUB_TOKEN or GH_TOKEN (or `gh auth token`) for GitHub; LeetCode is public.
Run by .github/workflows/update-profile.yml every day, or by hand from the repo root."""
import json
import os
import re
import subprocess
import sys
import html
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree

ME = "A-RYAN-1"
LEETCODE = "DarKKKKKnight"
MEDIUM_FEED = "https://medium.com/feed/@aryan0deshmukh"
MAX_POSTS_LISTED = 6
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
SKIP_OWNERS = {ME.lower(), "biagiopietro"}
WHAT = {
    "sustainable-computing-io/kepler": ("Kepler", "Energy use per Kubernetes pod and container, as Prometheus metrics"),
    "prometheus-operator/prometheus-operator": ("Prometheus Operator", "Kubernetes operator for Prometheus and Alertmanager"),
    "hluk/CopyQ": ("CopyQ", "Clipboard manager with advanced features (C++, Qt)"),
    "actualbudget/actual": ("actual", "Local-first personal finance and budgeting app (TypeScript)"),
    "ONEARMY/community-platform": ("community-platform", "Precious Plastic community platform (React, TypeScript)"),
    "rubyforgood/casa": ("casa", "Multi-tenant case management for CASA child-advocacy programs (Ruby on Rails)"),
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


def open_prs(tok):
    """{repo: [pr numbers]} for open, non-draft PRs of ours in other people's repos."""
    out = defaultdict(list)
    page = 1
    while True:
        d = gh_get(f"/search/issues?q=author:{ME}+is:pr+is:open+draft:false&per_page=100&page={page}", tok)
        for it in d["items"]:
            repo = it["repository_url"].split("/repos/")[1]
            if repo.split("/")[0].lower() not in SKIP_OWNERS and not it.get("draft"):
                out[repo].append(it["number"])
        if len(d["items"]) < 100:
            break
        page += 1
    return {r: sorted(n) for r, n in out.items()}


def live_projects(tok):
    repos = gh_get(f"/users/{ME}/repos?per_page=100&type=owner", tok)
    return sum(1 for r in repos if not r["fork"] and r["name"] != ME and (r.get("homepage") or r.get("has_pages")))


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


def ranked(prs, info):
    return sorted(prs.items(), key=lambda kv: (-info[kv[0]]["stargazers_count"], kv[0]))


def display(repo, info):
    if repo in WHAT:
        return WHAT[repo]
    desc = (info.get("description") or "").strip()
    if len(desc) > 90:
        desc = desc[:87].rsplit(" ", 1)[0] + "..."
    return repo.split("/")[1], desc


def pr_table(prs, info):
    rows = ["| # | Project | What it is | Merged PRs | Stars |", "|---|---|---|---|---|"]
    for i, (repo, nums) in enumerate(ranked(prs, info), 1):
        name, desc = display(repo, info[repo])
        links = " ".join(f"[#{n}](https://github.com/{repo}/pull/{n})" for n in nums)
        badge = f"![stars](https://img.shields.io/github/stars/{repo}?style=flat-square&logo=github&color=lightgrey)"
        rows.append(f"| {i} | [{name}](https://github.com/{repo}) | {desc} | {links} | {badge} |")
    return "\n".join(rows)


def logo_row(prs, info):
    out = ['<p align="center">']
    for repo, _ in ranked(prs, info):
        name, _d = display(repo, info[repo])
        owner = repo.split("/")[0]
        out.append(f'  <a href="https://github.com/{repo}"><img src="https://github.com/{owner}.png?size=64" width="48" height="48" alt="{name}" title="{name}"></a>')
    out.append("</p>")
    return "\n".join(out)


def open_line(open_map, info):
    """One link per repo, straight to its newest open PR; the rest counted and linked to the search."""
    ordered = sorted(open_map, key=lambda r: (-info[r]["stargazers_count"], r))
    if not ordered:
        return ""
    parts = []
    for repo in ordered[:6]:
        nums = open_map[repo]
        label = f"{display(repo, info[repo])[0]} #{nums[-1]}" + (f" (+{len(nums) - 1})" if len(nums) > 1 else "")
        parts.append(f"[{label}](https://github.com/{repo}/pull/{nums[-1]})")
    rest = len(ordered) - 6
    if rest > 0:
        q = f"https://github.com/pulls?q=is%3Apr+is%3Aopen+draft%3Afalse+author%3A{ME}+-user%3A{ME}"
        parts.append(f"[{rest} more]({q})")
    joined = ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]
    return f"Open now: {joined}."


def prs_links(repo, nums):
    return ", ".join(f"[PR #{n}](https://github.com/{repo}/pull/{n})" if i == 0 else f"[#{n}](https://github.com/{repo}/pull/{n})"
                     for i, n in enumerate(nums))


def fixes_block(prs, info):
    """Top 3 repos by live stars that have a story file in stories/. Reports higher-starred repos without one."""
    chosen, missing = [], []
    for repo, nums in ranked(prs, info):
        f = ROOT / "stories" / (repo.replace("/", "__") + ".md")
        if f.exists():
            if len(chosen) < 3:
                chosen.append((repo, nums, f.read_text(encoding="utf-8").strip().replace(chr(13) + chr(10), chr(10))))
        elif len(chosen) < 3:
            missing.append(repo)
    out = []
    for repo, nums, body in chosen:
        body = re.sub(r"^(- Result: .*)$", lambda m: m.group(1) + " " + prs_links(repo, nums), body, flags=re.M)
        out.append(body)
    for repo in missing:
        print(f"MISSING STORY: {repo} ranks in the top 3 by stars but has no stories/{repo.replace('/', '__')}.md")
    return (chr(10) * 2).join(out), missing


XERJ_URL = f"https://hub.xerj.org/contributors/{ME}"


def xerj_block(prs):
    """Repos indexed in the XERJ Corpus Hub, read from the contributor page title ('<repo> corpus')."""
    try:
        with urllib.request.urlopen(urllib.request.Request(XERJ_URL, headers={"User-Agent": "profile-updater"}), timeout=30) as r:
            page = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError):
        return None
    names = re.findall(r"<title>[^<]*?: ([^<:]+?) corpus \| XERJ Hub</title>", page)
    if not names:
        return None
    links = []
    for n in names:
        repo = next((r for r in prs if r.split("/")[1].lower() == n.lower()), None)
        links.append(f"[{n}](https://github.com/{repo})" if repo else n)
    return (f"My merged work is indexed in the [XERJ Corpus Hub]({XERJ_URL}) as worked reference code for AI coding agents: "
            + ", ".join(links) + ".")


def medium_posts():
    """Posts from the Medium RSS feed, newest first: (title, link, subtitle). None when the feed cannot be read,
    so the caller keeps whatever the README already shows. The feed holds the 10 newest posts only."""
    try:
        req = urllib.request.Request(MEDIUM_FEED, headers={"User-Agent": "Mozilla/5.0 profile-refresh"})
        with urllib.request.urlopen(req, timeout=30) as r:
            root = ElementTree.fromstring(r.read())
    except (urllib.error.URLError, ElementTree.ParseError, TimeoutError, OSError) as e:
        print(f"medium feed unavailable ({e}); keeping the Writing list as it is")
        return None
    ns = {"c": "http://purl.org/rss/1.0/modules/content/"}
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").split("?")[0].strip()
        body = it.findtext("c:encoded", namespaces=ns) or ""
        m = re.search(r"<h4[^>]*>(.*?)</h4>", body, re.S)
        sub = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).replace("\xa0", " ").strip() if m else ""
        if title and link:
            out.append((title, link, sub))
    return out or None


def writing_list(posts):
    lines = []
    for title, link, sub in posts[:MAX_POSTS_LISTED]:
        if len(sub) > 150:
            cut = sub[:150]
            sub = (cut[: cut.rfind(" ")] if " " in cut else cut).rstrip(",;:") + "..."
        lines.append(f"- [{title}]({link})" + (f": {sub}" if sub else ""))
    return "\n".join(lines)


def replace_block(text, name, body):
    return re.sub(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", lambda m: m.group(1) + body + m.group(2), text, flags=re.S)


def check_stories(tok):
    """--check-stories: print the top-3 repos by stars that still need a story file; write nothing. Exit 1 if any."""
    prs = merged_prs(tok)
    info = {r: gh_get(f"/repos/{r}", tok) for r in prs}
    _fixes, missing = fixes_block(prs, info)
    return 1 if missing else 0


def main():
    tok = token()
    if "--check-stories" in sys.argv:
        raise SystemExit(check_stories(tok))
    prs = merged_prs(tok)
    n_prs = sum(len(v) for v in prs.values())
    lc = leetcode()
    live = live_projects(tok)
    raw = README.read_bytes().decode("utf-8")
    text = raw.replace("\r\n", "\n")
    writing = text.split("## Writing", 1)[-1].split("## ", 1)[0]
    feed = medium_posts()
    shown = len(set(re.findall(r"medium\.com/@aryan0deshmukh/[\w-]+", writing)))
    before = re.search(r"(\d+) engineering posts", text)
    # the feed lists only the 10 newest posts, so the count never goes down
    posts = max(len(feed), int(before.group(1)) if before else 0) if feed else shown
    items = [(str(n_prs), "open-source PRs merged", f"{len(prs)} projects, linked below"),
             (str(lc["total"]), "LeetCode problems", f'{lc["easy"]} easy, {lc["medium"]} medium, {lc["hard"]} hard'),
             (str(posts), "engineering posts", "on production debugging"),
             (str(live), "projects live", "deployed on free tiers")]
    ASSETS.mkdir(exist_ok=True)
    for n, c in THEMES.items():
        (ASSETS / f"numbers-{n}.svg").write_text(numbers_svg(c, items), encoding="utf-8")
        (ASSETS / f"leetcode-{n}.svg").write_text(leetcode_svg(c, lc), encoding="utf-8")
    alt = f"{n_prs} open-source PRs merged, {lc['total']} LeetCode problems solved, {posts} engineering posts, {live} projects live"
    text = re.sub(r'(<!-- numbers:start -->.*?<img alt=")[^"]*(")', lambda m: m.group(1) + alt + m.group(2), text, flags=re.S)
    opened = open_prs(tok)
    info = {r: gh_get(f"/repos/{r}", tok) for r in set(prs) | set(opened)}
    text = replace_block(text, "logos", logo_row(prs, info))
    text = replace_block(text, "contrib", pr_table(prs, info))
    text = replace_block(text, "open", open_line(opened, info))
    fixes, _missing = fixes_block(prs, info)
    if fixes:
        text = replace_block(text, "fixes", fixes)
    xerj = xerj_block(prs)
    if xerj:
        text = replace_block(text, "xerj", xerj)
    if feed and "<!-- writing:start -->" in text:
        text = replace_block(text, "writing", writing_list(feed))
    new = text.replace("\n", "\r\n") if "\r\n" in raw else text
    if new != raw:
        README.write_bytes(new.encode("utf-8"))
    print(f"{n_prs} merged PRs in {len(prs)} repos; leetcode {lc['total']}; {live} live; {posts} posts")


if __name__ == "__main__":
    main()
