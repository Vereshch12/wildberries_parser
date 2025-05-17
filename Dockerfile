FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ARG USE_AI=false
COPY requirements-ai.txt .
RUN if [ "$USE_AI" = "true" ]; then pip install --no-cache-dir -r requirements-ai.txt; fi
RUN rm -rf /root/.cache/huggingface
COPY src/ src/
COPY .env ./
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
RUN if [ "$USE_AI" = "true" ]; then \
    pip install huggingface_hub && \
    python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='sentence-transformers/all-MiniLM-L6-v2', cache_dir='/tmp/hf_cache')" && \
    rm -rf /tmp/hf_cache; \
fi
CMD ["python", "src/main.py"]