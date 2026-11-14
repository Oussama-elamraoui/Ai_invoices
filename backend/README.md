# Invoice AI API

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env
# Add your OpenAI API key to .env to enable invoice extraction.
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive API docs are at
`http://localhost:8000/docs`. The development database is created at
`storage/invoice_ai.db` on startup. You can point `DATABASE_URL` at PostgreSQL
instead. `AUTO_CREATE_TABLES` is enabled for local development; disable it only
when your deployed database schema is provisioned separately.

Set `CORS_ORIGINS` to a JSON array of frontend origins when the frontend runs
on a different host or port. ZIP uploads are limited to 100 MB and can contain
up to 100 supported invoice files (PDF, PNG, JPG, JPEG, or WEBP).

## Frontend API

All application routes use the `/api/v1` prefix:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/uploads/` | Upload an invoice ZIP and start a processing job |
| `GET` | `/jobs/` | List recent processing jobs |
| `GET` | `/jobs/{job_id}` | Read job status and processing counts |
| `GET` | `/invoice-drafts/job/{job_id}` | List drafts produced by a job |
| `GET` | `/invoice-drafts/{draft_id}` | Read a draft for review |
| `PATCH` | `/invoice-drafts/{draft_id}` | Save reviewed draft data |
| `POST` | `/invoice-drafts/{draft_id}/approve-corrections` | Approve suggested corrections |
| `POST` | `/invoice-drafts/{draft_id}/correct-items` | Correct invoice line items |
| `POST` | `/invoice-drafts/{draft_id}/confirm` | Confirm a draft as an invoice |
| `GET` | `/entities/suppliers` | List/search active suppliers |
| `POST` | `/entities/suppliers` | Create a supplier |
| `GET` | `/entities/suppliers/{supplier_id}` | Read a supplier |
| `GET` | `/entities/clients` | List/search active clients |
| `POST` | `/entities/clients` | Create a client |
| `GET` | `/entities/clients/{client_id}` | Read a client |
| `GET` | `/invoices/` | List confirmed invoices; optional `job_id` and `status` filters |
| `GET` | `/invoices/{invoice_id}` | Read an invoice and its line items |
| `GET` | `/health` | Check API availability |

List endpoints accept `skip` and `limit` query parameters where applicable.
Invoice extraction runs in the background; poll the job endpoint and then load
its drafts to display progress and review results.

## Run the frontend

The React app lives in the sibling `frontend/` project. From the workspace
root, start it in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The React dashboard uses the API at
`http://localhost:8000/api/v1` by default. To change it, set
`VITE_API_URL` in `frontend/.env.local` before starting Vite, for example:

```dotenv
VITE_API_URL=http://localhost:8000/api/v1
```
