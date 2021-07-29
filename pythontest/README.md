# Running Tests

Tests are performed using pytest.
To execute, perform the following command:

- `source ./pypath && pytest tests/`

Notes:

- `./add_inits` will recursively add `__init__.py` to each test dir.
- `pypath` will set the PYTHONPATH variable within the context on your terminal. Ensure the PYTHONPATH variable in the script points to both your local branch for testing, **../python/** as well as to your built library, **/path/to/build** (in that order). Optionally, include the standard **$PYTHONPATH** variable too. For example, `PYTHONPATH=../python/:/path/to/build/:$PYTHONPATH`.
- Remember `venv` when running against a dev build.
