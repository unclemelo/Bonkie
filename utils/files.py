import json
from pathlib import Path
from typing import Any

def read_json(path: str | Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str | Path, data: Any, *, indent: int | None = 4) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
