FROM python:3.11-slim AS builder


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmagic1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


WORKDIR /app


COPY . .


RUN mkdir -p uploads/temp uploads/temp_youtube downloads logs bin


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production


EXPOSE 8000


RUN groupadd -r toolbox && useradd -r -g toolbox toolbox
RUN chown -R toolbox:toolbox /app
USER toolbox


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "run:app"] 