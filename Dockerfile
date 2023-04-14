FROM python:3.10-slim-buster
LABEL maintainer="Jessica Walkenhorst"
LABEL description="Meeting-Attendance-Organizer"

ARG PIP_VERSION="21.2.1"
ARG POETRY_VERSION="1.2.0"


RUN pip3 install -q "pip==$PIP_VERSION"
RUN pip3 install -q "poetry==$POETRY_VERSION"

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

WORKDIR /home/

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src/

RUN poetry install --without dev

EXPOSE 7860

ENTRYPOINT ["poetry", "run", "streamlit", "run", "src/maorganizer/ui.py", "--server.port", "7860"]
