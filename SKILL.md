---
name: event-vetting
description: Decide whether a B2B event, conference sponsorship, trade show, field dinner, webinar or partner event is worth the money — and prove it with numbers. Scores an event against the buyer's ICP, counts real ICP prospects from an attendee or delegate list, and converts the price into required pipeline, required opportunities, required meetings and the close rate the spend implies. Use this whenever someone is weighing up an event sponsorship, comparing events, asking "is this worth it", building a half-year or annual event calendar, reviewing an event budget, analysing a delegate or attendee list, calculating event ROI or payback, or deciding whether to renew last year's sponsorship. Use it even when the person hasn't asked for a score — if there is an event and a price in the conversation, this is the right tool.
---

# Event Vetting

Most event decisions get made on vibes and defended after the fact. Most B2B teams say they can't attribute ROI back to events, and the reason is almost never the event — it is that nobody wrote down what the event had to produce before they bought it.

This skill fixes that in three moves: **score the room**, **count the prospects**, **do the arithmetic**. Each one works on its own, and they get stronger in that order as information arrives.

## Which mode you are in

Work out where the person is before doing anything else:

| They have | Do this | Section |
|---|---|---|
| An event name and a price | Score it and run the economics | A then C |
| A delegate / attendee list | Count ICP prospects, then economics | B then C |
| Both | All three, and produce a go / negotiate / decline | A, B, C, then D |
| A whole calendar to build | Score every candidate, rank by cost per fit point, then pick | A across the set |
| An event that already happened | Skip to the post-event read | E |

If you do not yet have the client's commercial inputs (margin, payback target, win rate, average contract value), **stop and get them** — see `assets/client-profile.md`. Everything in section C is meaningless without them, and inventing them produces confident nonsense. Asking for four numbers is cheap; a fabricated payback model that a CFO pulls apart is not.

---

## A. Score the room

Six dimensions, each 1–5, weighted, normalised to 0–100. The full anchors, the competitor keyword lists and the special cases are in `references/scoring-rubric.md` — read it before scoring anything, because the anchors are where the judgement actually lives.

| Dimension | Weight | The question |
|---|---|---|
| ICP Density | 25% | What share of the room is a real buyer |
| Meeting Mechanism | 25% | Can we get a scheduled 1:1, or only booth traffic |
| Seniority Fit | 15% | Decision-makers or practitioners |
| Competitive & Partner Presence | 15% | Who else is paying to be in that room |
| Data / List Rights | 10% | Do we get the attendee list, or just a scanner |
| Prior Performance | 10% | Did it work last time |

`score = SUMPRODUCT(values, weights) ÷ 5 × 100`

Because of the normalisation, one step on a 25% dimension moves the total 5 points; one step on a 10% dimension moves it 2. Tell the person that — it stops arguments about the dimensions that cannot change the answer.

Default tiers: **T1 Flagship ≥75 · T2 Core ≥58 · T3 Test ≥40 · T4 Decline below**.

**Competitive & Partner Presence is the one worth real research.** Open the event's sponsor / exhibitor / partner page and read it. It takes two minutes and it is the only dimension backed by other companies' money rather than your own opinion. When several events need scoring, dispatch parallel subagents — one per batch — rather than working through them serially.

**Cost per fit point** = all-in cost ÷ score. Useful for ranking, and only within a format. Comparing a $500 webinar to a $40,000 conference on this ratio is meaningless, because cost is the numerator and doing nothing always wins. Say so out loud when presenting it; someone will otherwise conclude the company should only run cheap webinars.

**Always report which dimensions are grounded and which are inferred.** A score built from the client's own data is worth arguing about. A score built from your reading of an event's name is worth checking. If most dimensions came from inference, lead with that.

---

## B. Count the ICP prospects

This is the upgrade that turns a judgement into a countable number, and it is available the moment an attendee or delegate list exists.

Run `scripts/analyze_delegates.py` — it parses a spreadsheet of delegates, handles the revenue-string mess (`£3 billion`, `1.2 billion`, `450m`, blanks), classifies job titles into economic buyers / champions / others, and reports counts under several definitions so you can see how sensitive the answer is.

```bash
python scripts/analyze_delegates.py <file.xlsx> --revenue-min 1000 --currency face
```

Read `references/delegate-analysis.md` before interpreting the output. Three decisions change the answer and must be made explicitly, once, and written down:

1. **Revenue at face value or FX-converted.** `£800m` is below a 1-billion bar at face value and above it in dollars. Face value is simpler and more conservative; it biases against non-USD events. Either is fine — silently mixing them is not.
2. **Blank revenue rows.** Excluded from the denominator, or counted as below the bar. Excluding is usually right; say which you did.
3. **Title filter on or off.** Revenue alone is looser and gives a bigger number. Revenue plus a finance-decision title is stricter and more defensible.

**Cost per ICP prospect** = all-in cost ÷ qualified prospects. This is the number that survives a CFO conversation, because every term in it is countable.

---

## C. Do the arithmetic

Five client inputs drive everything. Get them from finance, not from marketing, and use the *actual trailing* win rate rather than the aspirational one — this single substitution usually doubles the bar and is the most valuable thing this skill does.

```
required ARR       = all-in cost ÷ (gross margin × payback years)
required pipeline  = required ARR ÷ win rate
required wins      = required ARR ÷ average contract value
required opps      = required wins ÷ win rate
meeting target     = required opps ÷ meetings-to-opportunity rate    (round up)
break-even cost per won customer = ACV ÷ (1 ÷ (margin × payback))
required close rate = cost per ICP prospect ÷ break-even cost per won customer
```

`scripts/event_economics.py` runs the whole chain:

```bash
python scripts/event_economics.py --cost 41000 --margin 0.5 --payback 1.5 \
    --win-rate 0.15 --acv 80000 --meetings-to-opp 0.30 --icp-prospects 49
```

**The meeting target is the output that changes behaviour.** "This $41,000 sponsorship needs 16 pre-booked meetings" is an instruction a seller can act on. "$41,000 needs $364,444 of pipeline" is a number a marketer nods at.

**Required close rate is the output that wins the argument.** It converts a price into a testable claim: *this event needs 1.4% of everyone in the room who fits to become a customer.* People can reason about that. They cannot reason about a fit score.

Read `references/payback-model.md` for the derivations, the rounding trap when totalling across a portfolio, and how to answer the four questions a CFO always asks.

---

## D. The recommendation

End with a verdict, not a dashboard. One of four, with one sentence of reasoning and the number that drove it:

- **GO** — economics clear the bar and the access terms support the meeting target
- **NEGOTIATE** — right room, wrong terms. Name the specific asks: attendee list pre- and post-event, lead scanning included, speaking slot, extra passes, customer passes, meeting-room access, a minimum-attendance make-good clause. Most sponsorship contracts are negotiable and most buyers never ask.
- **DOWNGRADE** — right room, wrong tier. Attend instead of sponsor, or take the smaller package.
- **DECLINE** — with the specific number that killed it

When the answer is decline, give the alternative. "$45,800 on this expo buys seven executive dinners where every attendee is a buyer" lands; "the ICP fit is weak" does not.

**Name the risks the price hides.** The commonest three: attendance is a forecast not a commitment (ask for a minimum or a make-good), executive time is the scarcest input and is almost never budgeted, and an event with no named seller produces no pipeline however good the room is.

---

## E. After the event

The loop only closes if outcomes come back. Three things have to happen, in this order:

1. **Leads uploaded** to the CRM campaign within 24 hours, routed with an SLA.
2. **Follow-up sent** — personalised to every held meeting within 24 hours, nurture to scanned-not-met, no-show sequence to booked-not-held.
3. **Debrief filed** within 48 hours — attendance promised vs actual, meetings booked vs held, ICP-qualified leads, opportunities created, plus a renew / renegotiate / downgrade / kill verdict.

The order matters. Follow-up is time-critical and decays fast; the debrief closes the loop for next cycle. Put the debrief first and a tidy write-up starts standing in for actually contacting anyone. Then pipeline reads at T+30, T+60 and T+90.

Two things this unlocks: **Prior Performance** stops being a placeholder and starts discriminating, and **actual cost per opportunity** replaces the modelled one. Until a client has a dozen events with real outcomes, every score in section A is a hypothesis. Say so.

A useful discipline to recommend: **no debrief filed, no renewal approved.** It is the only forcing function that reliably works, because it attaches the paperwork to the money.

---

## Working with a portfolio

When scoring a whole calendar rather than one event:

- Rank by **cost per fit point within format** — conferences against conferences, dinners against dinners
- Flag any event whose spend is out of line with its tier; the most expensive line paired with the weakest score is almost always the finding
- Watch the **format mix**. Sponsored conferences are the most expensive way to buy a room. Partner co-hosted events and field dinners usually beat them on cost per qualified conversation, and most clients under-use both.
- Check **executive load**. Count the events each named executive is committed to. When one or two people appear on a third of the calendar, that is the binding constraint on the whole program, not budget.
- Sum required pipeline across the portfolio and compare it to the pipeline target. If events are expected to carry more pipeline than the whole company plans to generate, the calendar is wrong regardless of how each event scores.

Rounding up per event inflates portfolio totals — a $500 webinar still demands one opportunity. Quote portfolio figures from unrounded program-level maths and per-event figures rounded up. `references/payback-model.md` has the detail.

---

## Reference files

- `references/scoring-rubric.md` — the six dimensions, full anchors, competitor keyword lists, special cases, and how to research competitive presence
- `references/delegate-analysis.md` — ICP prospect definitions, revenue parsing, currency rules, title tiers, sample-size traps
- `references/payback-model.md` — derivations, the rounding trap, sensitivity, and the four CFO questions
- `assets/client-profile.md` — the inputs to collect before any of this works
