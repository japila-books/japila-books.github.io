ARG INSIDERS_TAG=7.0.1-insiders-2.0.0

FROM ghcr.io/squidfunk/mkdocs-material-insiders:${INSIDERS_TAG}

RUN python -m pip install --upgrade pip
RUN pip install --upgrade wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

