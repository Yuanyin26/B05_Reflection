FROM python:3.11-slim

WORKDIR /app/program/solution

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY src/ ./src/
COPY run.sh ./run.sh
RUN chmod +x /app/program/solution/run.sh

ENV DATA_ROOT=/input \
    OUTPUT_DIR=/output \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/program/solution/run.sh"]
CMD ["--task", "all"]
