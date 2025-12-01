=

# Laptop Price Predictor

A reproducible machine-learning project that predicts laptop prices from hardware specifications. Includes a FastAPI backend, Streamlit frontend, a scikit-learn model loader, and MongoDB persistence. Built for development and deployment.

## Key features

- Predict laptop price from structured specs via REST API
- Streamlit UI for interactive prediction and admin dashboard
- MongoDB-backed persistence for prediction history and analytics
- Simple in-memory TTL cache for repeated inferences
- Clear project layout with modular services, models, and repositories

## Repository structure (high level)

- src/ or laptop_price_predictor/ — application package
  - core/ — configuration, logging
  - models/ — ML wrapper & data schemas
  - repositories/ — DB interfaces (MongoDB)
  - routers/ — FastAPI routers
  - services/ — prediction business logic
  - utils/ — helpers, cache
- frontend/ — Streamlit apps
- ml_model/ — serialized model and artifacts (pkl)
- tests/ — unit tests
- requirements.txt, pyproject.toml, .env

Adjust paths if your layout differs.

## Quickstart (development)

1. Clone repository and change directory:
   ```bash
   git clone <your-repo-url>.git
   cd LAPTOP_PRICE_PREDICTOR
   ```

2. Create and activate virtualenv, install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env` (example keys):
   - MONGODB_URL
   - MONGODB_DB_NAME
   - MONGODB_COLLECTION_NAME
   - MODEL_PATH
   - DATA_PATH
   - APP_HOST, APP_PORT

4. Ensure ML artifacts exist at MODEL_PATH (e.g., ml_model/linear_regression.pkl).

5. Run FastAPI:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   API docs: http://localhost:8000/docs

6. (Optional) Run Streamlit UI:
   ```bash
   streamlit run frontend/app.py
   ```

## API (examples)

- POST /api/v1/prediction/predict — Accepts JSON with laptop specs, returns predicted price.
- GET /api/v1/prediction/predictions — List recent predictions.
- GET /api/v1/prediction/predictions/{id} — Fetch specific prediction.
- DELETE /api/v1/prediction/cache — Clear in-memory cache.
- Admin CRUD routes under `/api/v1/prediction/admin`.

Refer to your routers/ and models/ for exact request/response schemas.

## Development notes

- Use black/isort for formatting.
- Add unit tests under tests/ and run with pytest.
- For production caching / concurrency, replace in-memory cache with Redis or similar.
- Validate input schemas before deployment.

## Contributing

- Open issues for bugs or feature requests.
- Create PRs against main with tests and clear description.
- Follow commit message conventions and keep dependencies up-to-date.

## License

Specify your license here (e.g., MIT). Add LICENSE file to repository.
