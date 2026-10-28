#!/usr/bin/env python3
"""Parse a delegate / attendee list and count ICP prospects.

Handles the usual mess: mixed currencies, "1.2 billion" vs "450m" vs "2,300,000,000",
blank and placeholder revenue cells, header rows that aren't row 1.

Reports counts under every combination of the three definitional choices
(face-value vs FX, blanks excluded vs counted, title filter on vs off) so the
sensitivity of the answer is visible rather than buried.

Usage:
    python analyze_delegates.py delegates.xlsx
    python analyze_delegates.py delegates.xlsx --revenue-min 1000 --cost 30000 --acv 80000
    python analyze_delegates.py list.csv --sheet "2026 UK" --revenue-min 500
"""
import argparse, re, sys, json
from collections import Counter

FX = {"£": 1.27, "€": 1.08, "chf": 1.12, "kr": 0.092, "¥": 0.0067, "$": 1.0}

# Default buying committee for a finance-function buyer. Override with --titles-a / --titles-b.
TITLES_A = ["cfo", "chief financial", "chief accounting", "finance director",
            "group finance", "vp finance", "vice president finance", "cao"]
TITLES_B = ["head of finance", "head finance", "controller", "controlling", "fp&a",
            "financial planning", "head of financial", "director finance",
            "director of finance", "finance lead", "finance manager", "treasur"]

PLACEHOLDERS = {"", "-", "--", "n/a", "na", "none", "unknown", "tbc", "tbd", "?"}


def parse_revenue(raw, convert):
    """Return revenue in millions of the reporting currency, or None if unparseable."""
    if raw is None:
        return None
    t = str(raw).strip().lower().replace(",", "").replace("\xa0", " ")
    if t in PLACEHOLDERS:
        return None
    rate = 1.0
    if convert:
        for sym, r in FX.items():
            if sym in t:
                rate = r
                break
    m = re.search(r"(\d+(?:\.\d+)?)\s*(billion|bn|milliard|million|mn|b\b|m\b|k\b)?", t)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2) or ""
    if unit.startswith(("billion", "bn", "milliard")) or unit == "b":
        v *= 1000
    elif unit.startswith(("million", "mn")) or unit == "m":
        pass
    elif unit == "k":
        v /= 1000
    elif v > 1_000_000:          # bare figure that is clearly absolute currency
        v /= 1_000_000
    return v * rate


def tier(title, a_kw, b_kw):
    t = (title or "").lower()
    if any(k in t for k in a_kw):
        return "A"
    if any(k in t for k in b_kw):
        return "B"
    return "C"


def find_col(headers, *needles):
    for i, h in enumerate(headers):
        hl = str(h or "").lower()
        if any(n in hl for n in needles):
            return i
    return None


def load_rows(path, sheet=None):
    """Return (list_of_row_lists, sheet_name). Supports .xlsx/.xlsm and .csv/.tsv."""
    if path.lower().endswith((".csv", ".tsv")):
        import csv
        delim = "\t" if path.lower().endswith(".tsv") else ","
        with open(path, newline="", encoding="utf-8-sig") as f:
            return [list(r) for r in csv.reader(f, delimiter=delim)], path
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    names = [sheet] if sheet else wb.sheetnames
    out = []
    for nm in names:
        if nm not in wb.sheetnames:
            sys.exit(f"No sheet named {nm!r}. Available: {wb.sheetnames}")
        ws = wb[nm]
        rows = [[c.value for c in row] for row in ws.iter_rows()]
        out.append((nm, rows))
    return out, None


def analyse(rows, args, a_kw, b_kw):
    # locate the header row: first row containing something title-ish
    hdr_i = None
    for i, r in enumerate(rows[:15]):
        if find_col(r, "job title", "title", "position", "role") is not None:
            hdr_i = i
            break
    if hdr_i is None:
        return None
    hdr = rows[hdr_i]
    ci_title = find_col(hdr, "job title", "title", "position", "role")
    ci_co = find_col(hdr, "company", "organisation", "organization", "account", "employer")
    ci_rev = find_col(hdr, "turnover", "revenue", "sales", "income")

    people = []
    for r in rows[hdr_i + 1:]:
        if not r or all(v in (None, "") for v in r):
            continue
        title = r[ci_title] if ci_title is not None and ci_title < len(r) else None
        co = r[ci_co] if ci_co is not None and ci_co < len(r) else None
        rev = r[ci_rev] if ci_rev is not None and ci_rev < len(r) else None
        if not (title or co):
            continue
        people.append({"title": str(title or "").strip(),
                       "company": str(co or "").strip(),
                       "rev_raw": rev,
                       "tier": tier(title, a_kw, b_kw)})
    if not people:
        return None

    res = {"n": len(people), "titles": dict(Counter(p["tier"] for p in people)),
           "companies": len({p["company"].lower() for p in people if p["company"]}),
           "variants": {}}
    for conv in (False, True):
        for p in people:
            p["rev"] = parse_revenue(p["rev_raw"], conv)
        known = [p for p in people if p["rev"] is not None]
        blanks = len(people) - len(known)
        for unknown_small in (False, True):
            base = len(people) if unknown_small else len(known)
            if not base:
                continue
            ge = [p for p in known if p["rev"] >= args.revenue_min]
            ge_titled = [p for p in ge if p["tier"] in ("A", "B")]
            key = f"{'fx' if conv else 'face'}/{'blanks-as-small' if unknown_small else 'blanks-excluded'}"
            res["variants"][key] = {
                "qualified_revenue_only": len(ge),
                "qualified_revenue_and_title": len(ge_titled),
                "below_bar": base - len(ge),
                "pct_below_bar": round((base - len(ge)) / base * 100),
                "denominator": base,
                "blanks": blanks,
            }
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--sheet")
    ap.add_argument("--revenue-min", type=float, default=1000,
                    help="revenue bar in millions of reporting currency (default 1000 = $1B)")
    ap.add_argument("--cost", type=float, help="all-in event cost, to get cost per prospect")
    ap.add_argument("--acv", type=float, help="average contract value, for required close rate")
    ap.add_argument("--margin", type=float, default=0.5)
    ap.add_argument("--payback", type=float, default=1.5)
    ap.add_argument("--titles-a", help="comma-separated economic-buyer keywords (overrides default)")
    ap.add_argument("--titles-b", help="comma-separated champion keywords (overrides default)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    a_kw = [s.strip().lower() for s in args.titles_a.split(",")] if args.titles_a else TITLES_A
    b_kw = [s.strip().lower() for s in args.titles_b.split(",")] if args.titles_b else TITLES_B

    loaded, _ = load_rows(args.path, args.sheet)
    if isinstance(loaded, list) and loaded and isinstance(loaded[0], tuple):
        sheets = loaded
    else:
        sheets = [(args.path, loaded)]

    out = {}
    for name, rows in sheets:
        r = analyse(rows, args, a_kw, b_kw)
        if r:
            out[name] = r

    if not out:
        sys.exit("Could not find a header row with a job-title column in any sheet.")

    if args.json:
        print(json.dumps(out, indent=2))
        return

    bar = f"${args.revenue_min/1000:g}B" if args.revenue_min >= 1000 else f"${args.revenue_min:g}M"
    for name, r in out.items():
        print(f"\n=== {name} ===")
        print(f"  delegates {r['n']}   distinct companies {r['companies']}")
        t = r["titles"]
        print(f"  titles: A economic buyer {t.get('A',0)} | B champion {t.get('B',0)} | C other {t.get('C',0)}")
        print(f"\n  Revenue bar: {bar}")
        print(f"  {'definition':32s} {'rev only':>9s} {'rev+title':>10s} {'% below bar':>12s} {'blanks':>7s}")
        for k, v in r["variants"].items():
            print(f"  {k:32s} {v['qualified_revenue_only']:9d} {v['qualified_revenue_and_title']:10d}"
                  f" {v['pct_below_bar']:11d}% {v['blanks']:7d}")
        if args.cost:
            print(f"\n  Cost per ICP prospect at all-in cost ${args.cost:,.0f}:")
            for k, v in r["variants"].items():
                for label, n in (("rev only", v["qualified_revenue_only"]),
                                 ("rev+title", v["qualified_revenue_and_title"])):
                    if n:
                        cpp = args.cost / n
                        line = f"    {k:32s} {label:10s} ${cpp:>8,.0f}/prospect"
                        if args.acv:
                            be = args.acv * args.margin * args.payback
                            line += f"   -> needs {cpp/be*100:.2f}% to close"
                        print(line)
            if args.acv:
                be = args.acv * args.margin * args.payback
                print(f"\n  (break-even cost per won customer = ${be:,.0f})")
    print("\n  Pick ONE definition and apply it to every event, or the comparisons mean nothing.")


if __name__ == "__main__":
    main()
