ARG TAG

FROM squidfunk/mkdocs-material:${TAG}

RUN <<-EOF
    echo mkdocs-material tag: $TAG
    pip install --upgrade pip wheel setuptools
EOF

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

