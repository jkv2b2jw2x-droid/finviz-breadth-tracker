# Finviz Breadth Tracker

GitHub Actions automation for updating Finviz market breadth data.

The updater fetches `https://finviz.com/` and extracts only these values:

| Date | New High | New Low | Advancing | Declining |
| --- | --- | --- | --- | --- |

It writes the data to:

- `finviz_breadth.csv`
- `finviz_breadth.xlsx`
- `finviz_breadth_log.txt`

Rows use the New York market date. If a row for the current New York date already exists, the script updates it instead of adding a duplicate.

## Run Locally

```bash
python -m pip install -r requirements.txt
python finviz_breadth_updater.py
```

## GitHub Actions

The workflow is defined at `.github/workflows/update-finviz.yml`.

It supports manual runs with `workflow_dispatch` and scheduled weekday runs around 5:45 PM New York time after the US market close. The workflow commits only the generated breadth CSV, XLSX, and log file back to the repository.

## How to use this from another laptop

- Go to the GitHub repository.
- Open or download `finviz_breadth.xlsx`.
- To manually update it, go to Actions -> Update Finviz Breadth -> Run workflow.
- The original laptop does not need to be on.
- Python is only needed if you want to test the script locally.
- Excel is only needed to open the `.xlsx` file.
- The CSV file can also be opened in Excel as a backup.

## Transfer / portability

- The GitHub repository is the source of truth.
- The local folder is only a setup copy.
- After confirming the repo is pushed and GitHub Actions works, the local folder can be copied, zipped, moved to another laptop, or deleted.
- To move it to another laptop, either clone the GitHub repo or download it as ZIP.
- Do not copy this project into unrelated repos.

## Limitations

Finviz can block automated requests or change its page layout. In either case, the updater logs the failure and exits with a nonzero status instead of writing uncertain data.
