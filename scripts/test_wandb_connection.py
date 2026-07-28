"""One-off script to verify the W&B API key works end to end.

Run with: python scripts/test_wandb_connection.py
Requires WANDB_API_KEY set in .env (see .env.example).
"""

import os

from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("WANDB_API_KEY"):
    raise SystemExit(
        "WANDB_API_KEY not set. Copy .env.example to .env and fill in your key."
    )

import wandb

run = wandb.init(project="vision-grasp-research", name="connection-test")
run.log({"dummy_metric": 1})
run.finish()

print("W&B connection test succeeded. Check your dashboard for the 'connection-test' run.")
