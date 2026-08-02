"""OpenRouter client for System C. Makes calls, logs raw text, scores nothing.

WHY CALLS AND SCORING LIVE IN DIFFERENT FILES
---------------------------------------------
This module and system_c_run.py are the only code in the project that
touch the network. They write every reply verbatim to a JSONL log and
stop there. system_c_eval.py reads that log and never opens a socket.

That split is what makes the project's re-parse rule enforceable rather
than a promise: a parser bug found after the sealed test run can be
fixed and the frozen raw text re-read as many times as needed, without
the model ever being asked again. Re-parsing stored text cannot fish for
a better score from the model; re-calling could. So one is allowed and
the other is structurally impossible from here.

RETRIES: TRANSPORT ONLY, NEVER CONTENT
--------------------------------------
A timeout, a 429, or a 5xx is a network event and gets retried with
backoff -- the model never produced anything, so nothing is being
re-rolled. A reply that ARRIVES and then fails to parse is never
retried. Retrying malformed content would quietly turn a single-shot
baseline into a best-of-N one while still being described as zero-shot.

SAMPLING
--------
Each repeat is an independent single-turn completion with no prior
messages, so the five repeats of an image are genuinely five draws
rather than one conversation. Temperature is left at the API default
and `seed` is deliberately not set: spec section 5.4 is asking how much
out-of-the-box output varies run to run, and pinning the seed would
suppress exactly the thing being measured.
"""

import base64
import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from cornell_data import INTERIM, find_images
from system_c_prompt import API_FAIL, PROMPT_VERSION, SYSTEM_MSG

KEY_VAR = "OPENROUTER_API_KEY"
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o"

# Left unset on the request so the provider default (1.0) applies. Recorded
# as a string because "we did not send this parameter" is the fact worth
# preserving in the log, not a number we assumed.
TEMPERATURE = "api-default"
MAX_TOKENS = 400
TIMEOUT_S = 90

RETRIES = 3
BACKOFF_S = 2.0
CONCURRENCY = 4

RAW_JSONL = INTERIM / "system_c_raw.jsonl"


def client():
    """Build the OpenRouter client, or explain exactly what is missing."""
    load_dotenv()
    key = os.environ.get(KEY_VAR)
    if not key:
        raise SystemExit(
            f"{KEY_VAR} is not set.\n"
            f"Add it to .env as {KEY_VAR}=<your OpenRouter key>.\n"
            "Note it must NOT be stored as WANDB_API_KEY: system_b_train.py "
            "reads that variable and would try to authenticate to Weights & "
            "Biases with an OpenRouter key."
        )
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit("pip install openai  (OpenRouter speaks the OpenAI API)")
    return OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT_S)


def encode_image(path):
    """Read an image as a base64 data URL.

    Cornell images are already 640x480, so nothing is resized: the prompt
    tells the model that coordinates are in this exact frame, and
    resizing here would make that statement a lie.
    """
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def call_once(cli, pcd, repeat, path, prompt, tag):
    """One completion. Returns a record; raises nothing.

    Transport failures are retried with jittered backoff and, if they
    never succeed, come back as an API_FAIL record so the call is still
    counted rather than vanishing from the denominator.
    """
    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url",
             "image_url": {"url": encode_image(path), "detail": "high"}},
        ]},
    ]
    rec = {"pcd_id": pcd, "repeat": repeat, "tag": tag, "model": MODEL,
           "temperature": TEMPERATURE, "prompt_version": PROMPT_VERSION,
           "attempts": 0, "transport_errors": []}

    for attempt in range(1, RETRIES + 1):
        rec["attempts"] = attempt
        try:
            r = cli.chat.completions.create(
                model=MODEL, messages=messages, max_tokens=MAX_TOKENS)
            rec["text"] = r.choices[0].message.content or ""
            rec["finish_reason"] = r.choices[0].finish_reason
            rec["usage"] = ({"prompt": r.usage.prompt_tokens,
                             "completion": r.usage.completion_tokens}
                            if r.usage else None)
            rec["ts"] = time.time()
            return rec
        except Exception as e:                      # transport, not content
            rec["transport_errors"].append(f"{type(e).__name__}: {e}"[:200])
            if attempt < RETRIES:
                time.sleep(BACKOFF_S * (2 ** (attempt - 1)) + random.random())

    rec["text"] = None
    rec["outcome_override"] = API_FAIL
    rec["ts"] = time.time()
    return rec


def run_calls(jobs, prompt, tag, out_path=RAW_JSONL):
    """Run (pcd_id, repeat) jobs through the pool, appending to the JSONL.

    Records are appended as they complete, so an interrupted run keeps
    everything it already paid for. `tag` names the phase (dev, val,
    test, probe) so one log can hold several without ambiguity.
    """
    cli = client()
    images = find_images()
    missing = sorted({p for p, _ in jobs} - set(images))
    if missing:
        raise SystemExit(f"no image on disk for pcd ids: {missing[:10]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    done, records = 0, []
    with open(out_path, "a") as f:
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            futures = [pool.submit(call_once, cli, pcd, rep, images[pcd], prompt, tag)
                       for pcd, rep in jobs]
            for fut in futures:
                rec = fut.result()
                f.write(json.dumps(rec) + "\n")
                f.flush()
                records.append(rec)
                done += 1
                if done % 25 == 0 or done == len(jobs):
                    fails = sum(1 for r in records if r.get("text") is None)
                    print(f"  {done}/{len(jobs)} calls  ({fails} api_fail)")
    return records


def load_raw(tag=None, path=RAW_JSONL):
    """Read the raw log back, optionally filtered to one phase tag."""
    if not path.exists():
        raise SystemExit(f"{path} does not exist; run system_c_run.py first")
    out = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if tag is None or rec.get("tag") == tag:
            out.append(rec)
    return out
