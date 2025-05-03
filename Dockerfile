FROM python:3.13.3-alpine

LABEL maintainer="Hospital Backend DevOps Team"

ENV PYTHONUNBUFFERED=1

ARG DEV=false

WORKDIR /app

# Copy only requirements first to leverage caching
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --no-cache postgresql-client && \
    apk add --no-cache --virtual .build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install --no-cache-dir -r /tmp/requirements.dev.txt; \
    fi && \
    apk del .build-deps && \
    rm -rf /tmp && \
    adduser -D django-user

ENV PATH="/py/bin:$PATH"

# Copy application code (this layer is rebuilt only if app code changes)
COPY ./app /app

EXPOSE 8000

USER django-user