from tbdb.core.utils import root
from pathlib import Path
from typing import Any
import sqlite3

SCRIPTS: Path = root()

def execute_sqlscript(config: dict[str, Any], db_name: str) -> None:
  scriptfile: Path = SCRIPTS / f"configure_{db_name}.sql"
  conn = sqlite3.connect(config[db_name], isolation_level=None)
  try:
    conn.executescript(scriptfile.read_text(encoding="utf-8"))
    return None
  finally:
    conn.close()

def configure_tbdb(config: dict[str, Any]) -> None:
  scriptfile: Path = SCRIPTS / "configure_tbdb.sql"
  conn = sqlite3.connect(config["babel"], isolation_level=None)
  try:
    conn.execute("ATTACH DATABASE ? AS PUBMED", (config["pubmed"],))
    conn.execute("ATTACH DATABASE ? AS PMC_CAPTIONS", (config["pmc_captions"],))
    conn.executescript(scriptfile.read_text(encoding="utf-8"))
    return None
  finally:
    conn.execute("DETACH PUBMED")
    conn.execute("DETACH PMC_CAPTIONS")
    conn.close()

def clean_all(config: dict[str, Any]) -> None:
  # TODO: reenable after migration if finished... `execute_sqlscript(config, "babel")`
  execute_sqlscript(config, "pubmed")
  execute_sqlscript(config, "pmc_captions")
  configure_tbdb(config)  
  return None