#!/bin/bash

export PICCOLO_CONF="tests.piccolo_conf"

python -m pytest --cov=piccolo_cursor_pagination --ignore=example --cov-report xml --cov-report html --cov-fail-under 95 -s $@