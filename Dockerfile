ARG INSIDERS_TAG

FROM squidfunk/mkdocs-material-insiders:${INSIDERS_TAG}

RUN python -m pip install --upgrade pip
RUN pip install --upgrade wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

