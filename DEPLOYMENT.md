# Deployment Notes

## Production entrypoint

Run the app with:

```bash
gunicorn wsgi:application
```

Most platforms set `PORT` automatically. The Flask development server is still available locally with:

```bash
python3 server.py
```

## Environment variables

Set these on your hosting platform:

- `GEMINI_API_KEY`
- `PORT` (usually supplied by the platform)
- `APP_DATA_DIR` for persistent server-side app data
- `GRAPH_OUTPUT_DIR` if you want graph images somewhere specific
- `SORTED_MESSAGES_DIR` if you want saved messages somewhere specific
- `AI_BRAIN_DB_PATH` if you want the SQLite DB somewhere specific
- `EMAIL_ADDRESS`
- `EMAIL_APP_PASSWORD`

## What is now server-friendly

- Flask web app in `server.py`
- WSGI entrypoint in `wsgi.py`
- Generated graph files stored in a configurable data directory
- Sorted message output stored in a configurable data directory
- AI memory SQLite DB stored in a configurable data directory

## Remaining production recommendations

- Move from SQLite to Postgres if you want multi-instance hosting.
- Use cloud object storage for uploaded/generated files if you want durable shared storage.
- Keep `Allow AI extraction for unstructured files` disabled by default for privacy.
- Do not deploy `Streamlit UI.py` as your production frontend.
