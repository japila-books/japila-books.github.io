FROM ghcr.io/squidfunk/mkdocs-material-insiders:6.2.3-insiders-1.15.0

RUN python -m pip install --upgrade pip
RUN pip install --upgrade wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

