# Gayatri

This is log server works with chrome extension `savitri` for my experiment.

## Requirements
poetry(python 3.6.7 or above)

## Run

Install dependencies with 

```shell
poetry shell
poetry install
```

or, use `requirements.txt`.
```shell
pip install -r requirements.txt
```

Run app with following command.

```shell
uvicorn api:app
```

If you want detect changes in proejct, add `--reload` option

## Documents

To see built-in document, access to `/docs` path.
