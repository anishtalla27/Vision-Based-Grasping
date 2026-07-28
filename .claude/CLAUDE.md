# Session rules (hard rules, not suggestions)

## Canary
Every single message in this session/project must begin with the literal word
"Anish," before anything else. This is a canary the user relies on: if this
word is ever missing from the start of a response, it signals that context
got lost or compacted, and the user will restart the session. Do not drop
this rule after compaction, summarization, or a long gap in the
conversation — it applies for the rest of this project, not just one message.

## Project context
This is the "Vision-Informed Grasp Decision Prediction" sub-project (pillar 1
of a larger senior research project: Adaptive Robotic Grasping). Source of
truth for scope/plan: `source_of_truth.md` in the project root. Treat it as
authoritative over any earlier drafts.

- Git/GitHub is the source of truth for code and the spec file.
- Google Drive is backup only (datasets, checkpoints, results), not primary storage.
- Hugging Face Hub is a fallback data source for datasets (Cornell Grasping,
  Jacquard), not the primary source.
- W&B (Weights & Biases) is used for experiment tracking once training begins.
