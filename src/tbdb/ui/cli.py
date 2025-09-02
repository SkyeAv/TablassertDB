from tbdb.core.main import new_tbdb
from pathlib import Path
import typer

app = typer.Typer(pretty_exceptions_show_locals=False)

@app.command()
def build(
  yamlfile: Path = typer.Option(
    ..., "--yamlfile", "-y", help="Path to NewPostgres YAML Configuration"
  )
) -> None:
  new_tbdb(yamlfile)
  return None

# wrapper for pyproject.toml entrypoint
def main() -> None:
  app()
  return None