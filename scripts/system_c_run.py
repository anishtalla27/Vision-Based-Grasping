"""Issue System C's API calls for one split. Writes raw text, scores nothing.

WHAT THIS SCRIPT ENFORCES
-------------------------
Two rules that the project has so far kept by hand are made structural
here, because System C is the one system where breaking them costs real
money and cannot be undone:

  * TEST IS CALLED ONCE. The first test run writes
    data/interim/system_c_test_called.json, and this script refuses
    outright if that file already exists. The sentinel is written BEFORE
    the calls go out, not after, so a run that crashes half way still
    counts as the run -- resuming would mean some images got more draws
    than others, which would silently bias the consistency numbers.
  * SPLITS ARE WHAT THEY SAY. Ids are taken from load_split() and
    re-checked against it, so a hand-edited id list cannot slip a train
    image into the test batch.

Nothing here parses a reply or computes a score. Every reply goes to
data/interim/system_c_raw.jsonl verbatim and system_c_eval.py reads it
back offline.

Usage:
    python scripts/system_c_run.py smoke     3 train images, 1 repeat
    python scripts/system_c_run.py probe     10 train images, contamination
    python scripts/system_c_run.py val       40 val images, 5 repeats
    python scripts/system_c_run.py test      123 test images, 5 repeats, ONCE
"""

import json
import random
import sys
import time

from cornell_data import INTERIM, load_split, split_ids
from system_c_client import MODEL, run_calls
from system_c_prompt import PROBE_PROMPT, PROMPT, PROMPT_VERSION

REPEATS = 5
SEED = 42

SMOKE_N = 3
PROBE_N = 10
VAL_CONFIRM_N = 40

TEST_SENTINEL = INTERIM / "system_c_test_called.json"


def pick(split, n):
    """A fixed, reproducible subset of one split."""
    ids = split_ids(split)
    if n is None or n >= len(ids):
        return ids
    return sorted(random.Random(SEED).sample(ids, n))


def assert_split(ids, split):
    """Hard-fail if any id is not in the split it is claimed to be in."""
    table = load_split()
    wrong = [p for p in ids if p not in table or table[p][1] != split]
    if wrong:
        raise SystemExit(f"SPLIT LEAK: {len(wrong)} ids are not {split}: {wrong[:10]}")
    print(f"Split hygiene OK: {len(ids)} images, all {split}.")


def seal_test():
    """Claim the one and only test run, or refuse."""
    if TEST_SENTINEL.exists():
        prev = json.loads(TEST_SENTINEL.read_text())
        raise SystemExit(
            "REFUSING: System C's test split has already been called, on "
            f"{time.ctime(prev['started'])} ({prev.get('calls')} calls, "
            f"model {prev.get('model')}, prompt {prev.get('prompt_version')}).\n"
            "The sealed run happens once. If something looks wrong with those "
            "results, the raw replies are in data/interim/system_c_raw.jsonl "
            "and can be re-parsed offline; they must not be re-requested."
        )
    ids = split_ids("test")
    assert_split(ids, "test")
    TEST_SENTINEL.parent.mkdir(parents=True, exist_ok=True)
    TEST_SENTINEL.write_text(json.dumps({
        "started": time.time(), "images": len(ids), "repeats": REPEATS,
        "calls": len(ids) * REPEATS, "model": MODEL,
        "prompt_version": PROMPT_VERSION,
    }, indent=2))
    print(f"Sealed test run claimed -> {TEST_SENTINEL}")
    return ids


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "smoke":
        ids, repeats, prompt, split = pick("train", SMOKE_N), 1, PROMPT, "train"
    elif phase == "probe":
        ids, repeats, prompt, split = pick("train", PROBE_N), 1, PROBE_PROMPT, "train"
    elif phase == "val":
        ids, repeats, prompt, split = pick("val", VAL_CONFIRM_N), REPEATS, PROMPT, "val"
    elif phase == "test":
        ids, repeats, prompt, split = seal_test(), REPEATS, PROMPT, "test"
    else:
        raise SystemExit(__doc__)

    if phase != "test":
        assert_split(ids, split)

    jobs = [(p, r) for p in ids for r in range(repeats)]
    print(f"\n{phase}: {len(ids)} images x {repeats} repeats = {len(jobs)} calls "
          f"to {MODEL} (prompt {PROMPT_VERSION})")
    records = run_calls(jobs, prompt, tag=phase)

    ok = sum(1 for r in records if r.get("text") is not None)
    print(f"\n{ok}/{len(records)} calls returned a reply. "
          f"Raw text appended to data/interim/system_c_raw.jsonl")
    if phase == "test":
        print("Test is now sealed. Score it with: python scripts/system_c_eval.py")


if __name__ == "__main__":
    main()
