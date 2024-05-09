#!/bin/bash

poetry run python -m src -d "$1" -e "$2" -c "$3" -t "$4"
