# Session rules (hard rules, not suggestions)

## Git / GitHub pushes
Claude may commit and push to GitHub in this project, but only as the user's
own identity: git author/committer "Anish Talla" and the GitHub account
`anishtalla27`. Never push or commit as Claude:
- Do NOT add `Co-Authored-By: Claude ...` or any Claude/AI attribution
  trailer to commit messages or PR descriptions.
- Do NOT change git user.name / user.email or switch GitHub accounts.
- No force-push unless the user explicitly asks for it.

The remote is configured as `origin` ->
https://github.com/anishtalla27/Vision-Based-Grasping.git

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
