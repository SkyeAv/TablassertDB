from tbdb.models.databases import pg_config
from tbdb.core.postgres import migrate
from tbdb.core.sqlite import clean_all
from pathlib import Path
from typing import Any

def new_tbdb(yamlfile: Path) -> None:
  config: dict[str, Any] = pg_config(yamlfile)
  clean_all(config)
  migrate(config)
  return None