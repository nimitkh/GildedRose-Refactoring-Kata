# NEW README

# Gilded Rose Refactoring Kata: Python solution

Solution to the Gilded Rose Python refactoring exercise. It refactors the legacy `update_quality`
code into small, testable, extendable pieces and adds the new **Conjured** item feature.
Work is confined to the `python/` directory, as requested.

## 0. Quick start

**Requirements:** Python 3.7 or newer, plus the kata's `requirements.txt` (`pytest`, `approvaltests`,
`pytest-approvaltests`, `coverage`).

```bash
cd python
pip install -r requirements.txt
pytest -v                        # runs EVERYTHING: my tests and the kata's approval test (can possible it passed others)
python texttest_fixture.py 30    # print a 30-day report of the sample inventory
```

Use `pytest`, not `python -m unittest`: the kata's approval test is a plain pytest function, which `unittest`
cannot collect (and it fails to import if `approvaltests` is missing). My own tests are standard `unittest`
classes, so they also run with `python -m unittest -v`.

**Note:** Please run using `python -m unittest -v`

## 1. Project layout

| File | Purpose |
|---|---|
| `gilded_rose.py` | All production code: `Item` (untouched), the updater classes, the registry and `GildedRose` |
| `tests/test_gilded_rose.py` | All my tests, written from the requirements specification |
| `texttest_fixture.py` | The kata's own command-line fixture (unchanged); the tests also run it |
| `tests/test_gilded_rose_approvals.py` | The kata's own approval test (unchanged). Its saved output is re-approved in the Conjured commit |

## 2. Design

```
GildedRose.update_quality()
        |  for each item
        v
get_updater(item)  --> exact name match?  --> AgedBrieUpdater / BackstagePassUpdater / SulfurasUpdater
                   --> name starts with "Conjured"? --> ConjuredItemUpdater
                   --> otherwise                    --> ItemUpdater (normal item)
        |
        v
updater.update(item)  =  update_sell_in(item)  then  update_quality(item)
```

This is the **Strategy pattern**: each kind of item owns its rules in a small class and `GildedRose` only
delegates. `Item` is not modified (the "goblin in the corner").

**To add a new item type:** write an `ItemUpdater` subclass overriding what differs, then register it in
`ITEM_UPDATERS` (or add a name rule in `get_updater`). No existing logic changes. Conjured itself is a
three-line class (`degrade_rate = 2`).

## 3. Testing strategy

All my tests live in `tests/test_gilded_rose.py` and are written from the requirements, one test per rule:

1. **Rule tests:** normal items, Aged Brie, Sulfuras, Backstage passes (every day boundary: 11, 10, 6, 5, 1, 0, -1),
   the 0 and 50 limits, and Conjured.
2. **30-day trajectories:** the exact quality and `sell_in` of the kata's sample items on every one of 30 days.
3. **Text fixture:** the tests run the kata's `texttest_fixture.main()` for the default 2 days and for 30 days and check the report.
4. **Registry tests:** `get_updater` returns the right strategy for each item name.
5. **The kata's approval test** keeps running unchanged. It compares the full 30-day report with a saved file. Because Conjured
   is new behaviour, the saved file is updated in the Conjured commit (see below).

The tests were written **before refactoring started** (commit 1) and run after **every** commit, so each
refactoring step is proven safe.

## 4. The refactoring journey (commit by commit)

Every commit keeps the whole suite green. Commits are small and touch one file at a time so the thought process is easy to follow.

| # | Commit | What changed | Why |
|---|---|---|---|
| 1 | `test: add requirement-based tests as a safety net` | `tests/test_gilded_rose.py` replaces the kata's failing placeholder test. No production change. | You cannot safely refactor legacy code without tests. |
| 2 | `refactor: replace magic strings and numbers with constants` | `"Aged Brie"`, `50`, `0` etc. become named constants. | Removes typo risk and makes rules readable. Zero logic change. |
| 3 | `refactor: extract increase/decrease quality helpers` | `increase_quality` / `decrease_quality` replace the repeated bounds checks. | The 0 and 50 limits are enforced in one place each. |
| 4 | `refactor: extract update_item and add guard clause for Sulfuras` | Loop body moved to `update_item`; `if SULFURAS: return`. | Sulfuras never changes, so every `!= SULFURAS` check disappears. |
| 5 | `refactor: one function per item type, if/elif instead of negated conditions` | `update_normal_item`, `update_aged_brie`, `update_backstage_passes`. | Replaces `!= A and != B` double negatives with a positive `if / elif / else`. |
| 6 | `refactor: separate sell_in and quality updates` | `is_expired`, `update_sell_in`, named backstage thresholds. | Single responsibility. Aging now happens first, so thresholds read `< 10` / `< 5` (the original `< 11` / `< 6` evaluated before aging). |
| 7 | `refactor: strategy classes per item type with a registry` | `ItemUpdater` and subclasses, `ITEM_UPDATERS`, `get_updater` (+ registry tests). | `update_quality` becomes a 3-line loop; new types never touch existing code. |
| 8 | `feat: add Conjured items` | `degrade_rate`, `ConjuredItemUpdater`, prefix match (+ Conjured tests, + re-approved approval file). | Shows the design is extendable: the feature is a few lines. |
| 9 | `chore: type hints, docstrings and README` | Type hints, docstrings, this README. | Professional finish, no behaviour change. |

### Re-approving the approval test (Conjured commit)

The kata's approval test stores the expected 30-day report. That report includes "Conjured Mana Cake", which the old code
treated as a normal item. After the Conjured change, exactly four lines differ and all of them are Conjured rows
(for example `Conjured Mana Cake, 2, 5` becomes `Conjured Mana Cake, 2, 4`).

## 5. Assumptions and ambiguities


The brief is vague in places, so these decisions are stated explicitly:

- **What counts as Conjured:** any item whose name starts with `"Conjured"`. The spec only gives the sample name `Conjured Mana Cake`.
- **How fast Conjured degrades:** by 2 per day, and by 4 once the sell-by date has passed (twice the normal rate in both cases).
- **Sulfuras:** never modified; its quality of 80 is not validated. Its `sell_in` is also left unchanged.
- **Out-of-range input quality** (above 50, for non-legendary items): behaviour is kept identical to the original code. For example, Aged Brie at 55 stays at 55 and a normal item at 55 drops to 54. Clamping such values to 50 would be a behaviour change that the brief did not ask for.
- **Backstage passes on the concert day:** `sell_in == 0` means the concert is today; the next update sets quality to 0, as in the original.
- **Matching is case-sensitive and exact** for Aged Brie, Backstage passes and Sulfuras, as in the original code.
- **`GildedRose` keeps its original signature** so existing callers and fixtures keep working.

# OLD README TEXT

# Gilded Rose starting position in Python

For exercise instructions see [top level README](../README.md)

Suggestion: create a python virtual environment for this project. See the [documentation](https://docs.python.org/3/library/venv.html)

## Run the unit tests from the Command-Line

```
python -m unittest
```

## Run the TextTest fixture from the Command-Line

For e.g. 10 days:

```
python texttest_fixture.py 10
```

You should make sure the command shown above works when you execute it in a terminal before trying to use TextTest (see below).


## Run the TextTest approval test that comes with this project

There are instructions in the [TextTest Readme](../texttests/README.md) for setting up TextTest. You will need to specify the Python executable and interpreter in [config.gr](../texttests/config.gr). Uncomment these lines:

    executable:${TEXTTEST_HOME}/python/texttest_fixture.py
    interpreter:python

## Run the ApprovalTests.Python test

This test uses the framework [ApprovalTests.Python](https://github.com/approvals/ApprovalTests.Python). You will need to install  Run it like this:

```
python tests/test_gilded_rose_approvals.py
```

You will need to approve the output file which appears under "approved_files" by renaming it from xxx.received.txt to xxx.approved.txt.
