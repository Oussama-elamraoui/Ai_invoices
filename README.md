# Invoice AI

This workspace contains two separate projects:

- [`backend/`](./backend/) — FastAPI API and invoice processing.
- [`frontend/`](./frontend/) — React dashboard.

## Start the backend

In a terminal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env
# Add an OpenAI API key to backend/.env to enable invoice extraction.
uvicorn app.main:app --reload
```

The API and interactive docs are at `http://localhost:8000` and
`http://localhost:8000/docs`.

## Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. It connects to the backend at
`http://localhost:8000/api/v1` by default. To change the URL, create
`frontend/.env.local` with:

```dotenv
VITE_API_URL=http://localhost:8000/api/v1
```

See [`backend/README.md`](./backend/README.md) for backend configuration and API
endpoints.

## Try the app with sample invoices

The synthetic test batch is [`backend/sample_invoices/sample_invoices.zip`](./backend/sample_invoices/sample_invoices.zip).
It includes complete invoices, mixed tax rates, an incomplete invoice for the
review flow, and a multi-page PDF. See
[`backend/sample_invoices/README.md`](./backend/sample_invoices/README.md) for
what to expect and a step-by-step test checklist.
