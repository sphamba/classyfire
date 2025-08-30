# ClassyFire 🔥

_Classify research articles_


## Requirements

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- Make


## Deploying the website locally

Follow these instructions to run Classy Fire locally. First, run:

```bash
make install
```

Then, edit the `.env` file in the root directory of the repository with the following content:

```env
CLASSYFIRE_LANG=en  # "en" or "fr"
```


Finally, run:

```bash
make run
```

The website will be available at [http://localhost:8501](http://localhost:8501).


## Importing CSV data

To import CSV data, run the following command:

```bash
uv run classyfire/scripts/import_csv.py <path-to-csv-file>
```
