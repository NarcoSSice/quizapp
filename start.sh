#!/bin/bash

alembic upgrade head

python app/main.py