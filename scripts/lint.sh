#!/bin/bash

SOURCES="piccolo_cursor_pagination tests"

isort $SOURCES
black $SOURCES
flake8 $SOURCES
mypy $SOURCES