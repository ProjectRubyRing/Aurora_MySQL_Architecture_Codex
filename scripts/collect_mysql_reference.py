"""Extract factual property tables, not prose, from the official MySQL 8.4 manual."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["server-system-variables", "innodb-parameters", "performance-schema-system-variables",
         "replication-options-replica", "replication-options-binary-log", "replication-options-gtids",
         "validate-password-options-variables", "server-options", "pluggable-authentication-system-variables"]


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.depth, self.rows, self.row, self.cell = [], 0, [], [], None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            if self.depth == 1:
                self.rows = []
        if self.depth == 1 and tag == "tr":
            self.row = []
        if self.depth == 1 and tag in ("td", "th"):
            self.cell = []
        if self.cell is not None and tag in ("p", "br", "li"):
            self.cell.append(" ")

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if self.depth == 1 and tag in ("td", "th") and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        if self.depth == 1 and tag == "tr":
            self.rows.append(self.row)
        if tag == "table":
            if self.depth == 1:
                self.tables.append(self.rows)
            self.depth = max(0, self.depth - 1)


def fetch(page):
    url = f"https://dev.mysql.com/doc/refman/8.4/en/{page}.html"
    try:
        with urlopen(url, timeout=30) as r:
            content = r.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as error:
        return page, {}, str(error)
    parser = Tables()
    parser.feed(content)
    result = {}
    for rows in parser.tables:
        props = {r[0]: r[1] for r in rows if len(r) == 2}
        name = props.get("System Variable")
        if not name:
            continue
        default = "; ".join(f"{k}: {v}" for k, v in props.items() if k.startswith("Default Value"))
        if default:
            result[name] = {"default": default, "scope": props.get("Scope", ""),
                            "dynamic": props.get("Dynamic", ""),
                            "url": url + "#sysvar_" + name,
                            "context": "Community MySQL 8.4 reference; not an Aurora runtime measurement"}
    return page, result, None


def main():
    combined, manifest = {}, []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for page, items, error in pool.map(fetch, PAGES):
            combined.update(items)
            manifest.append({"page": page, "count": len(items), "error": error})
            print(page, len(items), error or "OK", flush=True)
    payload = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "pages": manifest, "parameters": combined}
    (ROOT / "evidence" / "mysql84_reference_defaults.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
