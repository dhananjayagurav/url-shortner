# ---- stage 1: builder -- installs dependencies only ----
FROM python:3.12-slim AS builder
WORKDIR /build 

COPY requirements.txt ./
# builder stage
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- stage 2: final -- the actual runtime image ----
FROM python:3.12-slim 
WORKDIR /app 

# Bring in only the installed packages from the builder stage --
# none of pip's cache, none of the build tooling, none of requirements.txt itself.
COPY --from=builder /install /usr/local 

# App code, and what alembic needs to run migrations against this image later.
COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations

# Run as a non-root user -- not root inside the container, same as you
# wouldn't run a real server process as root.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

# Uses Python itself to hit the app's own /health endpoint --
# no need to install curl just for this one check.
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
