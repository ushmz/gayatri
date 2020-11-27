# Gayatri

This is API server works with chrome extension `savitri` 

## Requirements
poetry(python 3.8)

## Run

Install dependencies.

```shell
poetry shell
poetry install
```

Run app with following command.

```shell
uvicorn api:app --reload # If you want detect changes in proejct, add `--reload` option
```

## Documents

To see built-in document, access to `/docs` path.
