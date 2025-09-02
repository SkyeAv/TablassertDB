from pydantic import BaseModel, Field, FilePath, ValidationError
from ruamel.yaml.error import YAMLError
from ruamel.yaml import YAML
from pathlib import Path
from typing import Any

class NewPostgres(BaseModel):
    babel: FilePath = Field(...)
    pubmed: FilePath = Field(...)
    pmc_captions: FilePath = Field(...)

yaml = YAML()

def parse_yaml(yamlfile: Path, string_path: str) -> Any:
    try:
        with yamlfile.open("r") as f:
            return yaml.load(f)
    except FileNotFoundError:
        err: str = f"BUILD-CODE:1 | Config Not Found... {string_path}"
        raise FileNotFoundError(err)
    except PermissionError:
        err = f"BUILD-CODE:2 | Permission Denied... {string_path}"
        raise PermissionError(err)
    except YAMLError as e:
        fail: str = str(e)
        err = f"BUILD-CODE:3 | Yaml Parsing Error... {string_path}... {fail}"
        raise YAMLError(err)


def pg_config(yamlfile: Path) -> dict[str, Any]:
    string_path: str = yamlfile.as_posix()
    parsed: Any = parse_yaml(yamlfile, string_path)
    try:
        return NewPostgres.model_validate(parsed).model_dump()
    except ValidationError as e:
        fail: str = str(e)
        err: str = f"BUILD-CODE:4 | Yaml Failed Validation... {string_path}... {fail}"
        raise ValidationError(err)