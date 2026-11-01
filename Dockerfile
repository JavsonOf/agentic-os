FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY agentic_os ./agentic_os
# pdf: reading PDFs in the knowledge base. The data folder must exist and belong to "agent" before a
# volume is mounted there, otherwise Docker creates it owned by root and every save fails.
RUN pip install --no-cache-dir ".[anthropic,gemini,pdf]" && useradd --create-home agent \
    && mkdir -p /home/agent/data && chown agent:agent /home/agent/data
USER agent

ENV AGENTIC_OS_DATA_DIR=/home/agent/data
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["agentic-os", "serve", "--host", "0.0.0.0", "--port", "8000"]
