# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches listings using the request's description keywords, applies an optional size and inclusive price ceiling, then ranks matches by counting case-insensitive query-word matches in each listing's `title`, `description`, and `style_tags`; listings with zero matches are excluded and ties keep the original data order.
- **Inputs:** `description` (`str`); `size` (`str | None`, optional); `max_price` (`float | None`, optional). Size matching is case-insensitive and matches a complete size label or slash-separated component (so `M` matches `S/M` but `L` does not match `XL`); it does not use substring matches.
- **Returns:** Up to `SEARCH_RESULT_LIMIT` matching listing dictionaries, best match first. Each dictionary contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`; `brand` may be `None`.
- **When it has nothing:** Returns an empty list (`[]`) when no listings match.

### `suggest_outfit`

- **What it does:** Suggests one or two outfits combining the item being considered with pieces in the user's wardrobe.
- **Inputs:** `new_item` (listing `dict`); `wardrobe` (`dict` with an `items` list of wardrobe-item dictionaries).
- **Returns:** A non-empty `str` containing outfit suggestions; when the wardrobe has items, suggestions name pieces the user owns.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns general styling advice for `new_item` as a non-empty string.

### `create_fit_card`

- **What it does:** Writes a short, social-media-style caption about the item and its outfit suggestion.
- **Inputs:** `outfit` (`str`); `new_item` (listing `dict`).
- **Returns:** A two-to-four-sentence `str` caption that mentions the item, its price, and its platform once each, and describes its vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a descriptive fallback string instead of raising an error.

**Spec check:** Could another person implement these tools without asking for clarification? The search fields, matching rule, ranking rule, tie behavior, return shape, and empty cases are specified above.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, set `session["error"]` to a helpful message suggesting the user change their keywords, size, or price limit, then return the session without calling `suggest_outfit`. Otherwise, save the results in `session["search_results"]`, select the first result into `session["selected_item"]`, and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Use regular expressions to extract an optional `size ...` value and optional `under $...` price ceiling; use the remaining words as the description passed to `search_listings`.

**What moves through the session:** `query` and `wardrobe` are initialized first; parsed `description`, `size`, and `max_price` go in `session["parsed"]`; `search_listings` fills `session["search_results"]`; the first result goes in `session["selected_item"]`; then `suggest_outfit` fills `session["outfit_suggestion"]` and `create_fit_card` fills `session["fit_card"]`. If there are no results, `session["error"]` is set and the later fields remain empty.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two outfit ideas featuring the **Y2K Baby Tee — Butterfly Print**:

**1. Ultimate Y2K Streetwear**
Pair the baby tee with the **Baggy straight-leg jeans, dark wash** for a classic early-2000s proportion play. Layer the **Vintage black denim jacket** on top and finish with the **Chunky white sneakers** and **Black crossbody bag**.

**2. Edgy Contrast**
Style the cropped baby tee with the **Wide-leg khaki trousers**. Add the **Black combat boots** to ground the softer pink and purple tones of the butterfly graphic, and accessorize with the **Black crossbody bag**.

  Fit card: Channel your inner early 2000s icon by pairing this Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans and chunky white sneakers for the ultimate throwback streetwear vibe. It's listed on depop for just $18.00 and ready to upgrade your rotation. Grab it before it's gone!

2 model calls this session, 1540 prompt + 207 output tokens

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0), ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0)]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(' '.join(suggest_outfit(load_listings()[0], get_example_wardrobe()).split()))"
Here are two ways to style your new Vintage Levi's 501 Jeans: **Outfit 1: Casual Streetwear** * **Top:** White ribbed tank top * **Outerwear:** Vintage black denim jacket* **Shoes:** Chunky white sneakers * **Accessories:** Black crossbody bag **Outfit 2: Cozy & Classic** * **Top:**Oversized grey crewneck sweatshirt * **Accessories:** Brown leather belt * **Shoes:** Black combat boots
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(' '.join(create_fit_card('jeans with white sneakers', load_listings()[0]).split()))"
Nothing beats the character of broken-in denim, especially when it comes with that effortless 90s street style vibe. Throw on your favorite jeans with white sneakers and you've got an instantly cool, everyday look ready to go. Grab these Vintage Levi's 501 Jeans — Medium Wash for just $38.0 up on depop before someone else snags them!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
