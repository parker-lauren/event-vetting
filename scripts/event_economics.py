#!/usr/bin/env python3
"""Turn an event price into what it has to produce.

Usage:
    python event_economics.py --cost 41000 --margin 0.5 --payback 1.5 \
        --win-rate 0.15 --acv 80000 --meetings-to-opp 0.30

    # with a delegate count, adds cost per prospect and required close rate
    python event_economics.py --cost 30000 --win-rate 0.15 --acv 80000 --icp-prospects 49

    # compare planning vs aspirational win rate
    python event_economics.py --cost 41000 --win-rate 0.15 --alt-win-rate 0.30 --acv 80000

    # what is the most this event could be worth?
    python event_economics.py --win-rate 0.15 --acv 80000 --icp-prospects 50 --close-rate 0.01 --ceiling
"""
import argparse, math, json


def chain(cost, margin, payback, win, acv, m2o):
    arr = cost / (margin * payback)
    pipeline = arr / win
    wins = arr / acv
    opps = wins / win
    meetings = opps / m2o
    return {
        "all_in_cost": cost,
        "required_arr": arr,
        "required_pipeline": pipeline,
        "required_pipe_to_spend": pipeline / cost,
        "required_wins": wins,
        "required_opps_exact": opps,
        "required_opps": math.ceil(opps),
        "meeting_target_exact": meetings,
        "meeting_target": math.ceil(meetings),
        "break_even_cost_per_won_customer": acv * margin * payback,
    }


def money(x):
    return f"${x:,.0f}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cost", type=float, help="all-in event cost (fee + travel + swag + print)")
    p.add_argument("--margin", type=float, default=0.5, help="gross margin, e.g. 0.5")
    p.add_argument("--payback", type=float, default=1.5, help="payback target in YEARS")
    p.add_argument("--win-rate", type=float, required=True, help="ACTUAL trailing opp-to-won rate")
    p.add_argument("--alt-win-rate", type=float, help="second win rate to compare against")
    p.add_argument("--acv", type=float, required=True, help="average contract value / ARR per customer")
    p.add_argument("--meetings-to-opp", type=float, default=0.30)
    p.add_argument("--icp-prospects", type=int, help="qualified delegates from the attendee list")
    p.add_argument("--close-rate", type=float, help="assumed prospect-to-customer rate, for --ceiling")
    p.add_argument("--ceiling", action="store_true", help="compute max defensible spend instead")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    if a.ceiling:
        if not (a.icp_prospects and a.close_rate):
            p.error("--ceiling needs --icp-prospects and --close-rate")
        ceiling = a.icp_prospects * a.close_rate * a.acv * a.margin * a.payback
        out = {"icp_prospects": a.icp_prospects, "assumed_close_rate": a.close_rate,
               "max_defensible_spend": ceiling}
        if a.json:
            print(json.dumps(out, indent=2)); return
        print(f"\n{a.icp_prospects} qualified prospects x {a.close_rate*100:.2f}% close "
              f"x {money(a.acv)} ACV x {a.margin:.0%} margin x {a.payback}y payback")
        print(f"  MAX DEFENSIBLE SPEND: {money(ceiling)}")
        print("\n  Anything above this needs a higher close rate, a bigger room, or a lower price.")
        return

    if not a.cost:
        p.error("--cost is required unless using --ceiling")

    r = chain(a.cost, a.margin, a.payback, a.win_rate, a.acv, a.meetings_to_opp)

    if a.icp_prospects:
        r["icp_prospects"] = a.icp_prospects
        r["cost_per_icp_prospect"] = a.cost / a.icp_prospects
        r["required_close_rate"] = r["cost_per_icp_prospect"] / r["break_even_cost_per_won_customer"]

    if a.alt_win_rate:
        alt = chain(a.cost, a.margin, a.payback, a.alt_win_rate, a.acv, a.meetings_to_opp)
        r["alternative"] = {"win_rate": a.alt_win_rate,
                            "required_pipeline": alt["required_pipeline"],
                            "required_opps": alt["required_opps"],
                            "meeting_target": alt["meeting_target"]}

    if a.json:
        print(json.dumps(r, indent=2)); return

    print(f"\nALL-IN COST {money(a.cost)}")
    print(f"  inputs: margin {a.margin:.0%} | payback {a.payback}y | win rate {a.win_rate:.1%} "
          f"| ACV {money(a.acv)} | meetings->opp {a.meetings_to_opp:.0%}\n")
    print(f"  required ARR from this event      {money(r['required_arr'])}")
    print(f"  REQUIRED PIPELINE                 {money(r['required_pipeline'])}"
          f"   ({r['required_pipe_to_spend']:.1f}x spend)")
    print(f"  required wins                     {r['required_wins']:.2f} customers")
    print(f"  required opportunities            {r['required_opps']}   (exact {r['required_opps_exact']:.1f})")
    print(f"  MEETING TARGET                    {r['meeting_target']}   (exact {r['meeting_target_exact']:.1f})")
    print(f"  break-even cost per won customer  {money(r['break_even_cost_per_won_customer'])}")

    if a.icp_prospects:
        print(f"\n  ICP prospects on the list         {a.icp_prospects}")
        print(f"  COST PER ICP PROSPECT             {money(r['cost_per_icp_prospect'])}")
        print(f"  REQUIRED CLOSE RATE               {r['required_close_rate']*100:.2f}% "
              f"of the qualified room must become customers")

    if a.alt_win_rate:
        alt = r["alternative"]
        print(f"\n  At the alternative win rate of {a.alt_win_rate:.0%}:")
        print(f"    required pipeline               {money(alt['required_pipeline'])}")
        print(f"    required opportunities          {alt['required_opps']}")
        print(f"    meeting target                  {alt['meeting_target']}")
        print("    -> show both and make the choice of win rate an explicit decision.")

    print("\n  The meeting target is the line to give sales. The required close rate is the line to give finance.")
    print("  Per-event figures round UP; do not sum them across a portfolio — recompute from program totals.")


if __name__ == "__main__":
    main()
