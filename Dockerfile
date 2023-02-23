# встановлення базового образу - https://docs.docker.com/engine/reference/builder/#from
# https://medium.com/swlh/alpine-slim-stretch-buster-jessie-bullseye-bookworm-what-are-the-differences-in-docker-62171ed4531d
FROM python:3.11-slim-buster AS base
# додаємо макроінформацію - хто автор і до кого задавать питання
# - https://docs.docker.com/engine/reference/builder/#maintainer-deprecated
LABEL maintainer="Kostuantyn Zivenko <kos.zivenko@gmail.com>"
# за замовчення всі операції виконуються з правами рута. Це не добра практика.
# докладніше - тут https://habr.com/ru/post/448480/
# наступні шість рядків необхідні для стоврення користувача, який не є рутом
# докладно про ARG ENV - https://vsupalov.com/docker-arg-env-variable-gui
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl gettext libpq-dev zlib1g-dev libjpeg62-turbo-dev && \
    rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
ENV UID=${UID}
ENV GID=${GID}
# тут ми сворюємо користувача з ім'м docker_user, який не є рутом, і його UID за
# замовченням буде 1000 (раніше тут було ARG UID=1000 ENV UID=${UID}), він може бути
# замінений при старті контейнера передачою змінної або в файлі docker-compose.yaml
# або як аргумент команди docker
RUN useradd -m -u $UID docker_user
USER docker_user

ENV VIRTUAL_ENV=/home/docker_user/.venv
ENV PATH="${VIRTUAL_ENV}/bin:/home/docker_user/.local/bin:${PATH}"
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
RUN curl -sSL https://install.python-poetry.org | python3 -
# Create a virtual env in home directory.

WORKDIR /home/docker_user/redbot_project

COPY pyproject.toml .
COPY poetry.lock .



RUN poetry install

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY . .
CMD ["python3", "-m", "redbot.main"]
