#!/usr/bin/env python3
"""skillrule-viz: 將 skill 的 Gate/Drift/Rule/Logic check 視覺化。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

DEFAULT_ROOTS = [".opencode/skills", ".agents/skills"]
RULE_PATTERNS = {
    "gate": re.compile(r"\bGate\s*\d+|門檻|前置|pre-?audit|explicit consent", re.I),
    "drift": re.compile(r"\bdrift\b|漂移|hash|manifest|sha256|re-?audit", re.I),
    "rule": re.compile(r"\bRule\b|規則|Iron Law|硬規則|MUST|NEVER|不得|必須", re.I),
    "logic": re.compile(r"Logic check|驗證|evidence|證據|RED|GREEN", re.I),
}


@dataclass
class Node:
    id: str
    label: str
    type: str
    source: str
    detail: str = ""


@dataclass
class Edge:
    source: str
    target: str
    label: str


def slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "_", text).strip("_")
    return s[:60] or "node"


def find_skill(path_or_name: str, roots: Iterable[Path]) -> Path | None:
    p = Path(path_or_name).expanduser()
    if p.exists():
        return p / "SKILL.md" if p.is_dir() else p
    for root in roots:
        cand = root / path_or_name / "SKILL.md"
        if cand.exists():
            return cand
    return None


def collect_skills(roots: Iterable[Path]) -> list[Path]:
    out = []
    for root in roots:
        if not root.exists():
            continue
        for skill_md in root.glob("*/SKILL.md"):
            out.append(skill_md)
    return sorted(set(out))


def classify(line: str) -> str | None:
    for kind, pat in RULE_PATTERNS.items():
        if pat.search(line):
            return kind
    return None


def extract_nodes(skill_md: Path) -> list[Node]:
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    skill_name = skill_md.parent.name
    nodes: list[Node] = [Node(id=f"skill:{skill_name}", label=skill_name, type="skill", source=str(skill_md))]
    seen = set()
    for raw in text.splitlines():
        line = raw.strip().lstrip("-*#> ").strip()
        if len(line) < 4:
            continue
        kind = classify(line)
        if not kind:
            continue
        key = (kind, line[:120])
        if key in seen:
            continue
        seen.add(key)
        nid = f"{kind}:{skill_name}:{slug(line[:40])}:{len(seen)}"
        nodes.append(Node(id=nid, label=line[:90], type=kind, source=str(skill_md), detail=line))
    return nodes


def make_edges(nodes: list[Node]) -> list[Edge]:
    edges = []
    skill_nodes = [n for n in nodes if n.type == "skill"]
    for s in skill_nodes:
        for n in nodes:
            if n.type != "skill" and n.source == s.source:
                edges.append(Edge(source=s.id, target=n.id, label=n.type))
    return edges


def mermaid(nodes: list[Node], edges: list[Edge], title: str) -> str:
    lines = ["flowchart LR", f"  %% {title}"]
    style = {
        "skill": "#dbeafe", "gate": "#dcfce7", "drift": "#fef9c3", "rule": "#fee2e2",
        "logic": "#ede9fe", "manifest": "#ffedd5", "report": "#e0f2fe", "finding": "#fecaca",
    }
    for n in nodes:
        label = n.label.replace('"', "'").replace("\n", " ")
        lines.append(f'  {slug(n.id)}["{label}"]')
    for e in edges:
        lines.append(f"  {slug(e.source)} -->|{e.label}| {slug(e.target)}")
    for t, color in style.items():
        ids = [slug(n.id) for n in nodes if n.type == t]
        if ids:
            lines.append(f"  classDef {t} fill:{color},stroke:#333,stroke-width:1px;")
            lines.append(f"  class {','.join(ids)} {t};")
    return "\n".join(lines) + "\n"


def generic_mermaid() -> str:
    return """flowchart LR
  G0[Gate 0: 明確授權/意圖] --> G1[Gate 1: Pre-audit/盤點]
  G1 --> G2[Gate 2: RED/基線失敗]
  G2 --> G3[Gate 3: GREEN/最小修正]
  G3 --> G4[Gate 4: 清理/驗證]
  G4 --> G5[Gate 5: Re-audit/Drift check]
  G5 --> D{Drift?}
  D -->|No| OK[可交付/記錄]
  D -->|Yes| G2
  R[Rules: MUST/NEVER/硬規則] -.約束.-> G0
  R -.約束.-> G3
  R -.約束.-> G5
"""


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(path: Path, target: Path | None = None) -> dict:
    entries = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, rel = parts[0], parts[1].strip().lstrip("*")
        entries.append({"sha256": digest, "path": rel})
    drift = {"missing": [], "changed": [], "ok": [], "extra": []}
    base = target.resolve() if target and target.exists() else None
    if base:
        seen = set()
        for e in entries:
            p = (base / e["path"]).resolve()
            seen.add(p)
            if not p.exists():
                drift["missing"].append(e["path"])
            else:
                actual = sha256_file(p)
                if actual == e["sha256"]:
                    drift["ok"].append(e["path"])
                else:
                    drift["changed"].append(e["path"])
        # extra: files present but not in manifest (best-effort, top-level only)
        for p in base.rglob("*"):
            if p.is_file() and ".git" not in p.parts and p.resolve() not in seen:
                try:
                    drift["extra"].append(str(p.relative_to(base)))
                except Exception:
                    pass
    return {"path": str(path), "entries": entries, "drift": drift, "target": str(base) if base else None}


def parse_audit_report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    data = {"path": str(path), "verdict": None, "risk": None, "findings": [], "raw": {}}
    m = re.search(r"\|\s*Verdict\s*\|\s*`?([^|`]+)`?\s*\|", text, re.I)
    if m:
        data["verdict"] = m.group(1).strip()
    m = re.search(r"\|\s*Risk level\s*\|\s*([^|]+)\|", text, re.I)
    if m:
        data["risk"] = m.group(1).strip()
    m = re.search(r"Raw:\s*\*\*([^*]+)\*\*", text)
    if m:
        data["raw"]["summary"] = m.group(1).strip()
    json_path = path.with_suffix(".json")
    if json_path.exists():
        try:
            obj = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
            data["json"] = obj
            summary = obj.get("summary", {})
            data["raw"].update({k: summary.get(k) for k in ["total_issues", "project_findings", "score", "severity", "recommendation"] if k in summary})
        except Exception:
            pass
    # pull top rule rows
    for line in text.splitlines():
        if line.startswith("|") and "|" in line[1:]:
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 4 and cols[1] in {"HIGH", "MEDIUM", "LOW", "CRITICAL"}:
                data["findings"].append({"rule": cols[0], "severity": cols[1], "count": cols[2], "sample": cols[3]})
    return data


def nodes_from_manifest(manifest: dict) -> tuple[list[Node], list[Edge]]:
    nodes, edges = [], []
    mid = f"manifest:{slug(Path(manifest['path']).name)}"
    mlabel = f"manifest: {Path(manifest['path']).name}"
    drift = manifest.get("drift", {})
    drift_count = len(drift.get("missing", [])) + len(drift.get("changed", []))
    nodes.append(Node(mid, mlabel, "manifest", manifest["path"], f"entries={len(manifest.get('entries',[]))} drift={drift_count}"))
    for kind, items in [("missing", drift.get("missing", [])), ("changed", drift.get("changed", []))]:
        for item in items[:30]:
            nid = f"drift:{kind}:{slug(item)}"
            nodes.append(Node(nid, f"{kind}: {item}", "drift", manifest["path"], item))
            edges.append(Edge(mid, nid, kind))
    return nodes, edges


def nodes_from_report(report: dict) -> tuple[list[Node], list[Edge]]:
    nodes, edges = [], []
    rid = f"report:{slug(Path(report['path']).name)}"
    verdict = report.get("verdict") or "unknown"
    risk = report.get("risk") or "unknown"
    nodes.append(Node(rid, f"report: {Path(report['path']).stem}", "report", report["path"], f"verdict={verdict} risk={risk}"))
    if verdict and verdict.lower() != "unknown":
        vid = f"finding:verdict:{slug(verdict)}"
        nodes.append(Node(vid, f"verdict={verdict}", "finding", report["path"], verdict))
        edges.append(Edge(rid, vid, "verdict"))
    for f in report.get("findings", [])[:20]:
        nid = f"finding:{slug(f['rule']+f.get('sample',''))}:{len(nodes)}"
        nodes.append(Node(nid, f"{f['rule']} {f['severity']} x{f['count']}", "finding", report["path"], str(f)))
        edges.append(Edge(rid, nid, f.get("severity", "finding")))
    return nodes, edges


def write_report(out: Path, nodes: list[Node], edges: list[Edge], generic: str, data_mmd: str, extras: dict) -> None:
    rows = ["| type | label | source |", "|---|---|---|"]
    for n in nodes:
        if n.type == "skill":
            continue
        src = Path(n.source).as_posix()
        rows.append(f"| {n.type} | {n.label.replace('|','/')} | `{src}` |")
    extra_md = ["## Manifest/Drift/Report 摘要"]
    for m in extras.get("manifests", []):
        d = m.get("drift", {})
        extra_md.append(f"- manifest `{m['path']}`: entries={len(m.get('entries',[]))}, ok={len(d.get('ok',[]))}, changed={len(d.get('changed',[]))}, missing={len(d.get('missing',[]))}, extra={len(d.get('extra',[]))}")
    for r in extras.get("reports", []):
        extra_md.append(f"- report `{r['path']}`: verdict={r.get('verdict')}, risk={r.get('risk')}")
    if len(extra_md) == 1:
        extra_md.append("- （未提供 manifest/report）")
    out.joinpath("report.md").write_text(
        "# skillrule-viz 報告\n\n"
        f"產生時間：{datetime.now().isoformat(timespec='seconds')}\n\n"
        + "\n".join(extra_md) + "\n\n"
        "## 通用 Gate/Drift/Rule\n\n```mermaid\n" + generic + "```\n\n"
        "## 資料驅動視圖\n\n```mermaid\n" + data_mmd + "```\n\n"
        "## 規則表\n\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def write_graph(out: Path, nodes: list[Node], edges: list[Edge]) -> Path:
    graph = {"nodes": [asdict(n) for n in nodes], "edges": [asdict(e) for e in edges]}
    p = out / "graph.json"
    p.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    out.joinpath("graph.md").write_text(
        "# Graph ingest\n\n" + "\n".join(f"- {n.type}: {n.label}" for n in nodes), encoding="utf-8"
    )
    return p


def run_cmd(cmd: list[str], timeout: int = 300) -> dict:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"ok": p.returncode == 0, "cmd": cmd, "code": p.returncode, "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:]}
    except Exception as e:
        return {"ok": False, "cmd": cmd, "error": str(e)}


def maybe_graphify(out: Path, graph_json: Path, mode: str) -> dict:
    res = {"mode": mode}
    if mode in ("ingest", "style", "all", "cli"):
        res["graph_json"] = str(graph_json)
    if mode in ("cli", "all"):
        html_out = out / "graph.html"
        res["native_html_cmd"] = run_cmd(["graphify", "export", "html", "--graph", str(graph_json), "--output", str(html_out)])
        res["native_html"] = str(html_out) if html_out.exists() else None
        # also try to build a normal graphify-out in-place for compatibility
        res["graphify_out_cmd"] = run_cmd(["graphify", str(out / "graph-docs"), "--no-viz"])
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--roots", default=",".join(DEFAULT_ROOTS))
    ap.add_argument("--out", default="")
    ap.add_argument("--mode", choices=["generic", "data", "both"], default="both")
    ap.add_argument("--graphify", choices=["ingest", "cli", "style", "all"], default="all")
    ap.add_argument("--manifest", action="append", default=[], help="audit manifest sha256 檔案")
    ap.add_argument("--manifest-target", default="", help="manifest 驗證目標目錄")
    ap.add_argument("--report", action="append", default=[], help="audit 報告 .md/.json")
    args = ap.parse_args()

    roots = [Path(r).expanduser().resolve() for r in args.roots.split(",") if r.strip()]
    skill_mds = []
    if args.all or not args.skill:
        skill_mds.extend(collect_skills(roots))
    for s in args.skill:
        found = find_skill(s, roots)
        if found:
            skill_mds.append(found)
    skill_mds = sorted(set(skill_mds))
    if not skill_mds:
        raise SystemExit("No skills found. Use --skill <name> or --all with valid roots.")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = Path(args.out).expanduser().resolve() if args.out else Path.cwd() / "skillrule-viz-out" / ts
    out.mkdir(parents=True, exist_ok=True)

    nodes, edges = [], []
    for smd in skill_mds:
        ns = extract_nodes(smd)
        nodes.extend(ns)
        edges.extend(make_edges(ns))

    extras = {"manifests": [], "reports": []}
    manifest_target = Path(args.manifest_target).expanduser().resolve() if args.manifest_target else None
    for m in args.manifest:
        mp = Path(m).expanduser().resolve()
        if mp.exists():
            parsed = parse_manifest(mp, manifest_target)
            extras["manifests"].append(parsed)
            ns, es = nodes_from_manifest(parsed)
            nodes.extend(ns); edges.extend(es)
    for r in args.report:
        rp = Path(r).expanduser().resolve()
        if rp.exists():
            parsed = parse_audit_report(rp)
            extras["reports"].append(parsed)
            ns, es = nodes_from_report(parsed)
            nodes.extend(ns); edges.extend(es)

    generic = generic_mermaid()
    data_mmd = mermaid(nodes, edges, "skill data-driven rules") if nodes else "flowchart LR\n  empty[No rules extracted]\n"
    if args.mode in ("generic", "both"):
        out.joinpath("generic.mmd").write_text(generic, encoding="utf-8")
    if args.mode in ("data", "both"):
        out.joinpath("data.mmd").write_text(data_mmd, encoding="utf-8")
    write_report(out, nodes, edges, generic, data_mmd, extras)
    graph_json = write_graph(out, nodes, edges)
    result = {
        "out": str(out), "skills": [str(p) for p in skill_mds], "nodes": len(nodes), "edges": len(edges),
        "manifests": [m["path"] for m in extras["manifests"]], "reports": [r["path"] for r in extras["reports"]],
        "graphify": maybe_graphify(out, graph_json, args.graphify),
    }
    out.joinpath("result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
