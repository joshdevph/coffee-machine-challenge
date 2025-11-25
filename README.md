# Coffee Machine Challenge

FastAPI backend plus Vue control panel that simulates a coffee machine. It supports espresso-based drinks, container refills, state persistence (JSON, SQLite, or in-memory), Dockerized development, and a ready-to-import Postman collection.

## Quick start (Docker)

```bash
docker-compose up --build
```

- API: http://localhost:8000 (Swagger UI at `/docs`)
- Frontend: http://localhost:5173
- State persists in the `coffee_state` volume (`/data/state.db` by default).

## Running the backend locally

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # or source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `WATER_CAPACITY_ML` | `2000` | Capacity for the attached water container (ml). |
| `COFFEE_CAPACITY_G` | `500` | Capacity for the coffee container (g). |
| `STORAGE_BACKEND` | `json` | One of `json`, `sqlite`, `memory`. Docker compose uses `sqlite`. |
| `STORAGE_PATH` | `app/machine_state.json` or `machine_state.db` | File location for JSON/SQLite storage. |
| `STORAGE_DIR` | `app/` | Base directory to resolve `STORAGE_PATH` if it is not absolute. |

Example (SQLite with a custom path):

```bash
STORAGE_BACKEND=sqlite STORAGE_PATH=/tmp/coffee.db uvicorn app.main:app --reload
```

## Running the frontend locally

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Set `VITE_API_BASE_URL` (default `http://localhost:8000`) to point at the FastAPI instance. When running via Docker compose this is already set.

## Storage backends

- `json` (default): Simple JSON file with atomic writes.
- `sqlite`: Single-row table that holds the machine state for sturdier persistence. Enabled by default in `docker-compose.yml`.
- `memory`: Keeps state in-process only—useful for tests or ephemeral runs.

Switch backends by setting `STORAGE_BACKEND` and, if needed, `STORAGE_PATH`.

## API summary

| Method | Path | Description |
| --- | --- | --- |
| `GET /status` | Current container levels and latest message. |
| `POST /coffee/espresso` | Make one espresso (8g coffee, 24ml water). |
| `POST /coffee/double-espresso` | Make one double espresso (16g coffee, 48ml water). |
| `POST /coffee/americano` | Make one americano (16g coffee, 148ml water). |
| `POST /coffee/ristretto` | Make one ristretto (8g coffee, 16ml water). |
| `POST /containers/water/fill` | Body: `{ "amount_ml": number }`. Adds water with overflow validation. |
| `POST /containers/coffee/fill` | Body: `{ "amount_g": number }`. Adds coffee with overflow validation. |

Errors are human-readable when containers are empty, a fill would overflow, or unexpected exceptions occur.

## Postman collection

Import `coffee-machine.postman_collection.json` and set the `base_url` variable (default `http://localhost:8000`).

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## Nice-to-haves delivered

- Multiple storage backends (JSON, SQLite, memory) with a single env toggle.
- Targeted unit tests for recipes and storage persistence.
- Postman collection for quick manual checks.
- Updated Vue layout with a more polished control-panel aesthetic.

## Assumptions

- The machine boots with full standard containers (2 L water, 500 g coffee) unless capacities are overridden before the first run.
- The chosen storage backend is responsible for state durability; Docker compose mounts a volume so restarts keep state.
- Recipes are fixed to the provided amounts; new recipes can be added by extending `RECIPES` in `app/machine.py`.
