# Delegate list analysis

An attendee or delegate list turns a judgement into a count. It is the single most valuable input in event vetting and it is usually obtainable — organisers share prior-year lists to sell sponsorship, and current-year lists are a standard contract ask.

## The three decisions that change the answer

Make these once per client, write them down, and apply them everywhere. Silently mixing conventions is how two people get different numbers from the same file.

**1. Revenue at face value, or converted to a common currency.**
`£800 million` is below a 1-billion bar at face value and above it once converted (~$1.02B). Face value is simpler, more conservative, and requires no rate table — but it systematically biases against non-USD events, which matters if the client buys across regions. Converting is more accurate and needs a stated rate and date. Either is defensible. Pick one.

**2. Blank revenue rows.**
Exclude them from the denominator, or count them as below the bar. Excluding is usually right — it reports the qualified share *of what is known* rather than punishing incomplete data. But report the blank count alongside, because a list that is 40% blank is a weak basis for a $30,000 decision.

**3. Title filter on or off.**
Revenue alone is looser and produces a bigger prospect count. Revenue plus a decision-relevant title is stricter and more defensible in front of finance. Expect the strict definition to cut 10–30% of the count. Whichever you choose, apply it to every event or the comparisons are meaningless.

## Title tiers

Classify by keyword against the client's buying committee, not a generic seniority list. A typical three-tier split for a finance-function buyer:

- **A — economic buyer**: CFO, Chief Financial Officer, Chief Accounting Officer, Finance Director, Group Finance Director, VP Finance
- **B — champion / evaluator**: Head of Finance, Controller, Head of Controlling, FP&A, Financial Planning, Director of Finance, Treasury
- **C — other**: everything else

A and B together are normally the qualified set. A-only is a useful stricter cut when the client sells top-down.

Build the keyword list from the client's own closed-won titles if they have them. That beats any generic list.

## Cost per ICP prospect

```
cost per ICP prospect = all-in cost ÷ qualified prospects
```

Use **all-in cost**, not the sponsorship fee. Travel, swag, print, shipping and staff time are real; excluding them flatters every event equally and makes cross-format comparison worse.

Then convert it into a testable claim:

```
required close rate = cost per ICP prospect ÷ break-even cost per won customer
```

At a break-even of $60,000 per won customer, $500 per prospect means 0.83% of the qualified room has to become a customer; $1,000 per prospect means 1.67%. People can argue about whether 1% is achievable. Nobody can argue about a fit score.

## Traps

**Small lists.** A partial current-year list is not a forecast. A 21-person list from an event that drew 109 last year gives a cost per prospect five times too high. Report both the partial-list figure and the prior-year basis, and name attendance as the risk — then recommend asking the organiser for a minimum delegate commitment or a make-good clause. That converts the unknown into a contract term.

**Prior-year lists.** Usually the best available evidence, and usually fine — audiences are stickier than organisers admit. But check whether the venue, price or format changed.

**Registered vs attended.** Registration lists overstate. If the organiser reports both, use attended.

**Duplicate companies.** Several delegates from one account is a good sign for that account, not several prospects. Count qualified *accounts* as well as qualified people when the list is company-heavy — for enterprise sellers the account count is the more honest denominator.

## Running the script

```bash
python scripts/analyze_delegates.py delegates.xlsx \
    --revenue-min 1000 \
    --currency face \
    --unknown exclude \
    --title-filter on
```

It auto-detects the header row and the title / company / revenue columns, parses mixed revenue formats (`£3 billion`, `1.2 billion`, `450m`, `2,300,000,000`, blanks, dashes), classifies titles, and prints counts under every combination of the three decisions above — so the sensitivity is visible rather than hidden. Pass `--cost` to get cost per prospect and required close rate in the same run.
