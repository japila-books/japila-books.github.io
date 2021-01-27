ARG INSIDERS_TAG=6.2.6-insiders-1.16.1

FROM ghcr.io/squidfunk/mkdocs-material-insiders:${INSIDERS_TAG}

RUN python -m pip install --upgrade pip
RUN pip install --upgrade wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

