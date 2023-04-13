#!/bin/sh
poetry run flake8 --ignore=W605,W503 src/* tests/*
