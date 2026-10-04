FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 DATA_DIR=/data
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY frontend frontend
COPY tools tools
COPY data /srv/seed
RUN useradd -m app && mkdir /data && chown app /data
USER app
EXPOSE 8000
# ONE worker on purpose: sessions, one-time codes and rate limits live in memory.
CMD ["sh", "-c", "cp -n /srv/seed/* /data/ 2>/dev/null; exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --proxy-headers"]
