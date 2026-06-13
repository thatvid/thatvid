#!/usr/bin/env python3
"""
Extract "complete design" projects (description, design fee, completion year)
from the MTA Capital Program Dashboard open data on data.ny.gov.

The public dashboard at http://web.mta.info/capitaldashboard/CPDHome.html blocks
automated requests, but the same project-level data is published as Open Data via
a Socrata JSON API on data.ny.gov. This script targets the
"MTA Capital Dashboard Agencies Detail" dataset, which carries per-project,
per-phase records (Design / Procurement / Construction) including commitment
amounts, dates, and project descriptions.

NETWORK NOTE: data.ny.gov must be reachable. In a Claude Code web session this
means the environment's network policy must allow `data.ny.gov`.

USAGE
  # 1) First, inspect the real schema (column names vary by dataset version):
  python3 scripts/mta_design_extract.py --inspect

  # 2) Then extract complete-design rows to CSV (adjust column flags if needed):
  python3 scripts/mta_design_extract.py --out complete_design.csv

  # Override the dataset id or column mappings discovered in step 1:
  python3 scripts/mta_design_extract.py \
      --dataset kizb-nxtu \
      --phase-col phase --phase-value Design \
      --status-col status --complete-value Complete \
      --fee-col commitment_amount \
      --date-col actual_completion_date \
      --desc-col project_description
"""
import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request

DEFAULT_DOMAIN = "data.ny.gov"
# "MTA Capital Dashboard Agencies Detail" — project + phase level detail.
DEFAULT_DATASET = "kizb-nxtu"

# Heuristics used to auto-detect columns when explicit flags aren't given.
PHASE_HINTS = ("phase", "milestone", "category")
STATUS_HINTS = ("status", "state")
FEE_HINTS = ("commitment", "fee", "amount", "budget", "cost", "value")
DATE_HINTS = ("complet", "actual_end", "end_date", "finish", "date")
DESC_HINTS = ("description", "project_name", "scope", "title", "name")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mta-design-extract/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def base_url(domain, dataset):
    return f"https://{domain}/resource/{dataset}.json"


def inspect(domain, dataset):
    rows = fetch_json(base_url(domain, dataset) + "?$limit=3")
    if not rows:
        print("No rows returned.", file=sys.stderr)
        return
    cols = sorted({k for r in rows for k in r.keys()})
    print(f"Dataset {dataset} on {domain} — {len(cols)} columns:\n")
    for c in cols:
        sample = next((r[c] for r in rows if c in r and r[c] not in (None, "")), "")
        print(f"  {c:<35} e.g. {str(sample)[:60]}")
    print("\nSample record:\n")
    print(json.dumps(rows[0], indent=2)[:2000])


def pick(cols, hints, override):
    if override:
        return override
    low = {c.lower(): c for c in cols}
    for h in hints:
        for lc, orig in low.items():
            if h in lc:
                return orig
    return None


def year_of(val):
    if not val:
        return ""
    # Socrata dates look like 2019-06-30T00:00:00.000 ; also handle plain years.
    s = str(val)
    for i in range(len(s) - 3):
        chunk = s[i:i + 4]
        if chunk.isdigit() and chunk.startswith(("19", "20")):
            return chunk
    return ""


def extract(args):
    cols_sample = fetch_json(base_url(args.domain, args.dataset) + "?$limit=1")
    if not cols_sample:
        print("No data returned from dataset.", file=sys.stderr)
        return 1
    cols = list(cols_sample[0].keys())

    phase_col = pick(cols, PHASE_HINTS, args.phase_col)
    status_col = pick(cols, STATUS_HINTS, args.status_col)
    fee_col = pick(cols, FEE_HINTS, args.fee_col)
    date_col = pick(cols, DATE_HINTS, args.date_col)
    desc_col = pick(cols, DESC_HINTS, args.desc_col)

    print("Resolved columns:", file=sys.stderr)
    for label, c in [("phase", phase_col), ("status", status_col),
                     ("fee", fee_col), ("date", date_col), ("desc", desc_col)]:
        print(f"  {label:<8} -> {c}", file=sys.stderr)
    if not all([fee_col, date_col, desc_col]):
        print("\nCould not auto-detect required columns. Re-run with --inspect "
              "and pass --fee-col/--date-col/--desc-col explicitly.", file=sys.stderr)
        return 2

    # Pull all rows (paginate to be safe).
    rows, offset, page = [], 0, 50000
    while True:
        url = base_url(args.domain, args.dataset) + "?" + urllib.parse.urlencode(
            {"$limit": page, "$offset": offset})
        batch = fetch_json(url)
        rows.extend(batch)
        if len(batch) < page:
            break
        offset += page

    pv, cv = args.phase_value.lower(), args.complete_value.lower()
    out = []
    for r in rows:
        if phase_col and pv not in str(r.get(phase_col, "")).lower():
            continue
        if status_col and cv not in str(r.get(status_col, "")).lower():
            continue
        out.append({
            "description": r.get(desc_col, ""),
            "design_fee": r.get(fee_col, ""),
            "year": year_of(r.get(date_col, "")),
        })

    out.sort(key=lambda x: x["year"], reverse=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["description", "design_fee", "year"])
        w.writeheader()
        w.writerows(out)

    print(f"\nWrote {len(out)} complete-design rows to {args.out} "
          f"(from {len(rows)} total records).")
    for row in out[:10]:
        print(f"  {row['year']:<6} {str(row['design_fee']):>16}  {row['description'][:70]}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--domain", default=DEFAULT_DOMAIN)
    p.add_argument("--dataset", default=DEFAULT_DATASET)
    p.add_argument("--inspect", action="store_true",
                   help="Print the dataset's columns and a sample row, then exit.")
    p.add_argument("--out", default="complete_design.csv")
    p.add_argument("--phase-col"); p.add_argument("--phase-value", default="Design")
    p.add_argument("--status-col"); p.add_argument("--complete-value", default="Complete")
    p.add_argument("--fee-col"); p.add_argument("--date-col"); p.add_argument("--desc-col")
    args = p.parse_args()

    try:
        if args.inspect:
            inspect(args.domain, args.dataset)
            return 0
        return extract(args)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} from {args.domain} — is the dataset id correct and "
              f"is {args.domain} allowed by the network policy?", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Network error reaching {args.domain}: {e.reason}. In a Claude Code "
              f"web session, allow {args.domain} in the environment network policy.",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
