FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements-render.txt ./
RUN pip install --no-cache-dir -r requirements-render.txt
COPY quick_api.py quick_train.py preference_filters.py ./
COPY models/quick_v1/catalog.json models/quick_v1/ranker.txt ./models/quick_v1/
COPY data/recipe_families.json ./data/recipe_families.json
CMD ["python", "quick_api.py", "--model", "models/quick_v1", "--host", "0.0.0.0"]
