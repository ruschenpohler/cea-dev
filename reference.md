
<!-- module:base -->
# Reference: Base

## Git commit format
`[type]: [description] [severity]`

## Commit types
| Label | Scope |
|---|---|
| `feat:` | New capability |
| `output:` | New research output, figures, tables |
| `fix:` | Bug fix |
| `refactor:` | Restructuring, no behaviour change |
| `style:` | Formatting, lint, whitespace |
| `chore:` | Maintenance, deps, config, file moves |
| `test:` | New or updated tests |
| `docs:` | Documentation, README, docstrings |
| `data:` | Dataset changes, schema migrations |
| `infra:` | Tooling, CI/CD, platform setup |
| `revert:` | Reverts a previous commit |

## Severity scale
| Score | Definition | Example |
|---|---|---|
| 0 | Zero runtime impact. Cannot break anything. | `style: ruff format src/ [0]` |
| 1 | Zero runtime impact. Mechanical change. | `chore: update .gitignore [1]` |
| 2 | Low risk. Version bumps, existing tooling. | `chore: bump pandas 2.0→2.1 [2]` |
| 3 | Low risk. Moves/renames, no logic change. | `chore: move pipeline.py to src/legacy/ [3]` |
| 4 | Moderate. Adds/updates tests or docs. | `test: add fixture for CLI stacking [4]` |
| 5 | Moderate. Standard parameter change. | `feat: expand GBT grid to max_depth {3,4,5,6} [5]` |
| 6 | Structural. Touches core logic, preserves interface. | `refactor: extract feature_groups() [6]` |
| 7 | Substantial. New feature with downstream consumers. | `feat: add target-specific GDP lags [7]` |
| 8 | Critical. Fixes bug affecting published results. | `fix: use Y/Y lags instead of Q/Q [8]` |
| 9 | High stakes. Changes protocol or data source. | `feat: switch to bridge-equation fill [9]` |
| 10 | Existential. Could invalidate prior analysis. | `feat: replace sklearn GBT with EM-DFM [10]` |

## pre-commit.d contract
- The dispatcher owns `.git/hooks/pre-commit`. Never overwrite it.
- To add a pre-commit check, drop a numbered script into `.git/hooks/pre-commit.d/`.
- Naming: `NN-description.sh` where NN controls execution order. Lower = earlier.
- Fast/cheap checks get low numbers (01–30). Slow checks get high numbers (70–99).

## Session start protocol
1. `git status` — verify clean working tree.
2. `git checkout -b [task-slug]` — never work on main directly.
3. On completion: commit all work, set status `handover` in `impl-log.jsonl`, open PR.

## impl-log.jsonl schema
| Field | Type | Meaning |
|---|---|---|
| `timestamp` | string ISO 8601 | `YYYY-MM-DDTHH:MM:SS` |
| `impl-stage` | string | e.g. `"Phase 1.3, Rolling eval"` |
| `headline` | string | One-line summary |
| `notes` | string | What, why, blockers, decisions |
| `metrics` | object | Structured data: anything you might later sum/filter |
| `commit-ids` | string | Comma-separated git hashes. Empty if none. |
| `status` | string | `started`, `in-progress`, `completed`, `halted`, `failed`, `handover` |
| `severity` | integer [0,10] | Same scale as commits |

<!-- module:python -->
# Reference: Python

## uv discipline
- Never `pip install`. Always `uv sync` or `uv add <pkg>`.
- `pyproject.toml` owns deps. `uv.lock` is the reproducibility contract — always commit it.
- Upper-bound dependencies: `pandas>=2.0.0,<3.0.0`.
- Separate runtime / dev / optional groups.

## Ruff
- Config lives in `pyproject.toml` under `[tool.ruff]`. Do not duplicate elsewhere.
- Pre-commit hook runs automatically. Do not skip it.

## pytest
- Every non-trivial pure function in `src/` gets a unit test.
- Fixtures in `conftest.py`. Use `random.seed(42)` for determinism.
- Use `tmp_path` for all file I/O in tests.
- Test naming: state the outcome — `test_drops_countries_below_threshold`, not `test_filter_1`.
