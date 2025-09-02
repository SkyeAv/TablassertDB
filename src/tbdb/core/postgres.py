from tbdb.core.utils import root
from pathlib import Path
from typing import Any
from os import environ
import subprocess

def pgloader_query(config: dict[str, Any]) -> Path:
    loadfile: Path = root(False) / "CACHE" / "migrate_tbdb.load"
    loadfile.parent.mkdir(parents=True, exist_ok=True)
    query: str = f"""\
LOAD DATABASE
    FROM sqlite//:{config["babel"].as_posix()}
    TO postgresql://{environ("TBDB_USER")}@localhost:{environ("TBDB_PORT")}/{environ("TBDB_NAME")}

WITH include drop, create tables, create indexes, reset sequences, foreign keys

SET work_mem = '64MB', maintenance_work_mem = '16GB'
"""
    with loadfile.open("w", encoding="utf-8") as f:
        f.write(query)
    return loadfile

def migrate(config: dict[str, Any]) -> None:
    loadfile: Path = pgloader_query(config)
    loadfile_string: str = loadfile.as_posix()
    try:
        _ = subprocess.run(
            ["pgloader", loadfile_string],
            capture_output=True,
            text=True,
            check=True
        )
        return None
    except subprocess.CalledProcessError as e:
        fail: str = str(e)
        err: str = f"BUILD-CODE:6 | pgloader failed... {loadfile_string} ... {fail}"
        raise subprocess.CalledProcessError(err)