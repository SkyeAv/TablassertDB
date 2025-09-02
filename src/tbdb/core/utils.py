from functools import cache
from pathlib import Path
from os import environ

@cache
def root(sqlscripts: bool = True) -> Path:
    if sqlscripts:
        return environ["TBDB_SQL_PATH"]
    else:
        return Path.cwd()