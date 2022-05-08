#!/usr/bin/env bash
killall gcalctool /home/user/.cache/pypoetry/virtualenvs/user-database-tg-hpGiraXy-py3.10/bin/python &
poetry run uvicorn api_server:app --host 0.0.0.0 --app-dir=user_database_tg/api &
poetry run python user_database_tg/main.py &
ngrok http 8000 && fg
