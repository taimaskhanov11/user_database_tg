#!/usr/bin/env bash

poetry run uvicorn api_server:app --host 0.0.0.0 --app-dir=user_database_tg/apps/api &
poetry run python user_database_tg/main.py && fg
