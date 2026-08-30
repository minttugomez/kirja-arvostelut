# Pylint report
Report created with Claude LLM

Run against the final version:

```bash
$ pylint app.py db.py reviews.py users.py comments.py config.py
```

Result:

```
Your code has been rated at 10.00/10
```

## Configuration (`.pylintrc`)

Two checks are disabled project-wide:

| Check | Reason |
|---|---|
| `missing-module-docstring` (C0114) | Every module is small and its filename already describes its purpose (`db.py`, `reviews.py`, `users.py`, `comments.py`). A docstring would only repeat that. |
| `missing-function-docstring` (C0116) | Route and helper functions have short, descriptive names (`new_review`, `add_comment`, `check_csrf`, `any_blank`, …). A one-line docstring would restate the name. |

## Inline disables

`app.py` – the two error handlers:

```python
@app.errorhandler(403)
def forbidden(error):  # pylint: disable=unused-argument
```

Flask calls an error handler with the exception object as a positional
argument, so the parameter must exist even though this app does not use it
(it just flashes a message and redirects).

## Warnings that were fixed rather than suppressed

| Warning | File | Fix |
|---|---|---|
| `dangerous-default-value` (W0102) | `db.py` | `params=[]` → `params=()` (immutable default) |
| `consider-using-dict-items` (C0206) | `app.py` | iterate `review_classes.items()` instead of indexing by key |
| `no-else-return` (R1705) | `app.py` (`login`) | dropped the `else` after the `return` |

## Other tooling

`pycodestyle` (PEP 8) also passes with no warnings on all modules.
