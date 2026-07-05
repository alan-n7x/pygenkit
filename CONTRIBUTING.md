# Contributing

## Workflow

1. Create a branch from `main`
2. Make your changes
3. Run quality checks
4. Open a Pull Request
5. Wait for CI to pass
6. Merge after approval

## Quality checks

```bash
ruff check src/ tests/
mypy src/pygenkit/
pytest
```

All three must pass before opening a PR.

## Commit style

Use conventional commits:

```
feat: new feature
fix: bug fix
refactor: code change without fix or feature
docs: documentation only
ci: CI/CD changes
test: test additions or fixes
```

## Pull Request

- Keep PRs small and focused
- Link related issues
- Update README if needed
- Add tests for new functionality

## Adding a new generator

1. Create a generator class in `src/pygenkit/generators/`
2. Add Jinja2 templates in `src/pygenkit/templates/`
3. Register in `generators/orchestrator.py`
4. Add config fields in `models/config.py`
5. Write tests in `tests/test_generators.py`

## Adding a new validator

1. Create a module in `src/pygenkit/validators/`
2. Add the check function (accepts `root: str | Path`, returns `list[str]`)
3. Register in `validators/api.py`
4. Write tests

## Adding a new CLI command

1. Create the command function in `src/pygenkit/cli/commands/`
2. Export it in `cli/commands/__init__.py`
3. Register it in `cli/app.py`
4. Add a docstring for `--help` output
5. Write tests

## Release process

```bash
# Ensure main is up to date
git checkout main && git pull

# Verify readiness
pygenkit release-check

# Tag and push
git tag v$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
git push origin --tags
```

The Release workflow will build, test, create a GitHub Release, and publish to PyPI.
