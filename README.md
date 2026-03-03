# seedling

Copier template skeleton for minimal Python project generation.

## Template Structure

- Single template root: `template/`
- Mode selection: `cli_mode = none | command | repl`
- Optional AI bundle: `include_ai_workflow = true | false`

Common files are rendered once and mode differences are handled with Jinja conditionals and post-copy pruning tasks.

## Quickstart

From the `seedling` repo:

```bash
uv run --with copier copier copy . ./my-new-project --trust
```

## Non-Interactive Generation Examples

Set a reusable optional-target selection (all defaults enabled):

```bash
DEFAULT_JUSTFILE_TARGETS='["test-cov","e2e","pre-commit","commitizen","complexity","vulture","darglint","docstr-coverage","audit","bandit","radon","find-dupes","docs-frontmatter-fix"]'
```

### `cli_mode=none`

```bash
uv run --with copier copier copy . /tmp/seedling-none --trust \
  -d project_name='Seedling None Demo' \
  -d project_slug='seedling-none-demo' \
  -d package_name='seedling_none_demo' \
  -d cli_mode='none' \
  -d include_ai_workflow=true \
  -d justfile_targets="$DEFAULT_JUSTFILE_TARGETS"

cd /tmp/seedling-none
uv run pytest -q
```

### `cli_mode=command`

```bash
uv run --with copier copier copy . /tmp/seedling-command --trust \
  -d project_name='Seedling Command Demo' \
  -d project_slug='seedling-command-demo' \
  -d package_name='seedling_command_demo' \
  -d cli_mode='command' \
  -d cli_name='commanddemo' \
  -d include_ai_workflow=true \
  -d justfile_targets="$DEFAULT_JUSTFILE_TARGETS"

cd /tmp/seedling-command
uv run commanddemo hello --name matrix
```

### `cli_mode=repl`

```bash
uv run --with copier copier copy . /tmp/seedling-repl --trust \
  -d project_name='Seedling Repl Demo' \
  -d project_slug='seedling-repl-demo' \
  -d package_name='seedling_repl_demo' \
  -d cli_mode='repl' \
  -d cli_name='repldemo' \
  -d include_ai_workflow=true \
  -d justfile_targets="$DEFAULT_JUSTFILE_TARGETS"

cd /tmp/seedling-repl
uv run repldemo --help
uv run repldemo repl --help
```

### Minimal optional-target profile

```bash
uv run --with copier copier copy . /tmp/seedling-minimal --trust \
  -d project_name='Seedling Minimal Demo' \
  -d project_slug='seedling-minimal-demo' \
  -d package_name='seedling_minimal_demo' \
  -d cli_mode='command' \
  -d cli_name='mindemo' \
  -d include_ai_workflow=false \
  -d justfile_targets='[]'
```

### Questions

- `project_name`
- `project_slug` (derived from `project_name`, editable)
- `package_name` (derived from `project_slug`, editable)
- `cli_mode`: `none | command | repl`
- `cli_name` (derived from `project_slug`, asked only when `cli_mode != none`, editable)
- `include_ai_workflow`: `true | false`
- `justfile_targets` (single checkbox screen, all selected by default):
  - `test-cov`, `e2e`, `pre-commit`, `commitizen`, `complexity`, `vulture`
  - `darglint`, `docstr-coverage`, `audit`, `bandit`, `radon`, `find-dupes`
  - `docs-frontmatter-fix`

### Conditional Rules (Defined)

- `cli_mode=none`:
  - no `[project.scripts]` entry
  - `src/<package>/cli.py` and `tests/unit/test_cli.py` are pruned post-copy
- `cli_mode=command`:
  - Typer `hello` command generated
- `cli_mode=repl`:
  - Typer `hello` + Textual-backed `repl` command generated
- `include_ai_workflow=false` removes `.ai` post-copy
- `.ai/PLANS/*` is never generated
- Optional justfile targets are included only when selected in `justfile_targets`
