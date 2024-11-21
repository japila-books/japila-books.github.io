ARG INSIDERS_TAG

FROM squidfunk/mkdocs-material-insiders:${INSIDERS_TAG}

RUN <<-EOF
    echo Insider tag: $INSIDERS_TAG
    python -m pip install --upgrade pip
    pip install --upgrade wheel
EOF

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

