# ScholarMatch — Scholarship Discovery

A Streamlit application that helps students explore scholarships using their academic profile and funding preferences.

## Implemented features

- Country and degree normalization, field matching and CGPA filtering.
- Funding preferences, deadline information and heuristic match scores.
- Provider links, required documents and eligibility notes.
- An optional email digest through Resend.

The current matching system uses explicit rules and scoring rather than a trained recommendation model or an LLM. A match score is a ranking aid, not an acceptance probability or a guarantee of eligibility.

## Run locally

Use Python 3.12 in a virtual environment. From this repository's root:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Scholarship browsing does not require an email API key. For the optional digest, create a local `.env` file using `.env.example` and supply your own Resend key. Set `RESEND_FROM_EMAIL` to a sender permitted by your Resend account. Never commit credentials.

## Repository files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface and optional email integration |
| `matching.py` | Independently testable filtering, normalization and ranking |
| `scholarships_database_v2.csv` | Scholarship catalog |
| `requirements.txt` | Python dependencies |
| `.env.example` | Optional email configuration template |

There is no Activepieces workflow export in this repository; the application runs directly in Streamlit.

## How it works

The application loads the CSV, checks required columns, cleans values and normalizes profile fields. The matching module filters and ranks catalog entries without mutating the source. Known expired deadlines are excluded; undated entries stay visible for manual verification. The interface displays results and can email a digest when configured.

## Limitations

- The CSV is a maintained snapshot, not a live scholarship feed. Verify deadlines, funding and eligibility on each provider's official site.
- Field matching is heuristic and may include related subjects that require manual checking.
- Missing published CGPA thresholds do not establish eligibility.
- No measured recommendation-quality benchmark is published yet.

## Validation

```bash
python -m unittest discover -s tests -v
```

Tests cover alias normalization, CGPA boundaries, expired and unknown deadlines, funding tags, empty results, input immutability and a Streamlit search without email credentials. GitHub Actions runs the suite on Python 3.12. Direct dependency versions match the local validation environment; transitive dependencies are not locked.

## Next improvements

- Record catalog verification dates and explain each match's scoring components.
- Benchmark ranking against manually reviewed profiles.
- Deploy only after configuring the optional email integration for the intended audience.
