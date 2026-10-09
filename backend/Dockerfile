FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
# install deps, then drop pip/setuptools: the runtime never needs a package manager
RUN pip install --no-cache-dir -r requirements.txt \
 && pip uninstall -y pip setuptools wheel \
 && useradd --uid 10001 --no-create-home appuser

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

USER 10001
EXPOSE 8000

# migrate the schema, then serve
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
