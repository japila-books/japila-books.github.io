FROM astral/uv:python3.14-trixie

WORKDIR /docs

COPY pyproject.toml uv.lock ./

RUN uv pip install --system .

CMD ["zensical", "serve", "--config-file", "mkdocs.yml", "--dev-addr", "0.0.0.0:8000"]