"""Issue System D's API calls. Writes raw text plus the mark permutation; scores nothing.

Mirrors system_c_run.py: test is called ONCE (sentinel written before
the calls go out), ids are re-checked against the frozen split, every
reply is logged verbatim, and the evaluation script reads the log
offline. Two additions:

  * Each call gets its own random permutation of candidate numbering,
    drawn from a seeded RNG and stored in the record, so a "pick 1"
    bias cannot masquerade as a preference and so self-agreement is
    measured on the physical candidate, not on the number.
  * The rendered, marked image is saved next to the log so the exact
    pixels the model saw can be re-inspected.

Usage:
    python scripts/system_d_run.py dev      30 train images x 2 repeats
    python scripts/system_d_run.py test     123 test images x 5 repeats, ONCE
"""

import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from cornell_data import INTERIM, find_images
from system_c_client import CONCURRENCY, call_once, client
from system_c_run import assert_split, pick
from system_d_candidates import MENUS, candidates, render
from system_d_prompt import PROMPT, PROMPT_V2_EQUAL, PROMPT_VERSION, SYSTEM_MSG

import system_c_client
system_c_client.SYSTEM_MSG = SYSTEM_MSG        # call_once reads the module global

RAW_JSONL = INTERIM / "system_d_raw.jsonl"
MARKED = INTERIM / "system_d_marked"
TEST_SENTINEL = INTERIM / "system_d_test_called.json"
DEV_N, DEV_REPEATS, TEST_REPEATS = 30, 2, 5
SEED = 42


def run(split, ids, repeats, tag, menu="full"):
    images = find_images()
    rng = random.Random(SEED)
    MARKED.mkdir(parents=True, exist_ok=True)
    cli = client()
    jobs = []
    for pcd in ids:
        cands = candidates(images[pcd], menu)
        for rep in range(repeats):
            if not cands:
                jobs.append((pcd, rep, None, None))
                continue
            order = list(range(len(cands)))
            rng.shuffle(order)
            out = MARKED / f"{tag}_{pcd:04d}_r{rep}.png"
            render(images[pcd], cands, order, out, uniform=(menu == "equal"))
            jobs.append((pcd, rep, order, out))
    print(f"{tag}: {len(ids)} {split} images x {repeats} repeats = {len(jobs)} jobs "
          f"({sum(1 for j in jobs if j[2] is None)} with no candidates, not called)")

    def one(job):
        pcd, rep, order, path = job
        if order is None:
            return {"pcd_id": pcd, "repeat": rep, "tag": tag, "text": None,
                    "outcome_override": "no_candidates", "order": None, "ts": time.time()}
        prompt = (PROMPT_V2_EQUAL if menu == "equal" else PROMPT).format(k=len(order))
        rec = call_once(cli, pcd, rep, path, prompt, tag)
        rec["order"] = order
        rec["menu"] = menu
        rec["prompt_version"] = PROMPT_VERSION
        rec["marked_image"] = str(path)
        return rec

    with open(RAW_JSONL, "a") as f, ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        for i, rec in enumerate(pool.map(one, jobs), 1):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if i % 25 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)}")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "dev"
    menu = sys.argv[2] if len(sys.argv) > 2 else "full"
    if menu not in MENUS:
        raise SystemExit(f"menu must be one of {MENUS}")
    # The original System D run is tagged plainly ("dev_v2", "test"); the
    # sparse-menu follow-ups carry the menu name in the tag and sentinel.
    suffix = "" if menu == "full" else f"_{menu}"
    if phase == "dev":
        ids = pick("train", DEV_N)
        assert_split(ids, "train")
        reps = DEV_REPEATS if menu == "full" else 1
        run("train", ids, reps, f"dev_{PROMPT_VERSION}{suffix}", menu)
    elif phase == "test":
        sentinel = TEST_SENTINEL if menu == "full" else \
            INTERIM / f"system_d_test_called{suffix}.json"
        if sentinel.exists():
            raise SystemExit(f"{sentinel} exists: this System D test run has already "
                             "been made and may not be repeated.")
        ids = pick("test", None)
        assert_split(ids, "test")
        sentinel.write_text(json.dumps({"ts": time.time(), "prompt": PROMPT_VERSION,
                                        "menu": menu, "n_images": len(ids),
                                        "repeats": TEST_REPEATS}))
        run("test", ids, TEST_REPEATS, f"test{suffix}", menu)
    else:
        raise SystemExit("usage: system_d_run.py dev|test [full|sparse|equal]")


if __name__ == "__main__":
    main()
