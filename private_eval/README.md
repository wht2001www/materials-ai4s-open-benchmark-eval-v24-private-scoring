# Standalone deterministic oracles

Each question has its own `tasks/MSxx/MSxx-Qx/private_eval/oracle.py`.

Run any file after copying it out of this repository:

```bash
python oracle.py --workspace /path/to/question-workspace
```

The workspace must contain the manifest-verified `inputs/` and the candidate `output/`.
The script uses only the Python standard library, never imports a shared local module,
never executes the submitted `analyze.py`, prints one JSON score record, and exits 0
when hard gates pass, 1 when they fail, or 2 for invalid input/invocation.

`DeterministicArtifactScore` is 0–80. The separate 0–20 blind Judge score is intentionally
outside these deterministic scripts.
