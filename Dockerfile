FROM python:3.12

WORKDIR /fastapi-survival-game
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev
COPY . .
CMD ["faststream", "run", "--workers", "1", "app.application:app"]
