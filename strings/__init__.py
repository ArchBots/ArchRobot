import sys
from pathlib import Path
from typing import List

import yaml

BASE_DIR = Path(__file__).resolve().parent
LANGS_DIR = BASE_DIR / "langs"

languages = {}
commands = {}
languages_present = {}


def get_command(value: str) -> List:
    return commands["command"][value]


def get_string(lang: str):
    if lang not in languages:
        lang = "en"
    
    class SafeDict(dict):
        def __getitem__(self, key):
            if key in self:
                return dict.__getitem__(self, key)
            if key in languages.get("en", {}):
                return languages["en"][key]
            return f"[{key}]"
        
        def get(self, key, default=None):
            if key in self:
                return dict.__getitem__(self, key)
            if key in languages.get("en", {}):
                return languages["en"][key]
            return default if default is not None else f"[{key}]"
    
    return SafeDict(languages[lang])


for file in BASE_DIR.iterdir():
    if file.suffix == ".yml":
        with file.open(encoding="utf8") as f:
            commands[file.stem] = yaml.safe_load(f)


eng_file = LANGS_DIR / "eng.yml"
if not eng_file.exists():
    print("ERROR: Base language file eng.yml is missing")
    sys.exit(1)

with eng_file.open(encoding="utf8") as f:
    languages["eng"] = yaml.safe_load(f)

languages["en"] = languages["eng"]

languages_present["eng"] = languages["eng"].get("name", "English")
languages_present["en"] = languages_present["eng"]


for file in LANGS_DIR.iterdir():
    if file.suffix != ".yml" or file.name == "eng.yml":
        continue

    lang = file.stem

    with file.open(encoding="utf8") as f:
        languages[lang] = yaml.safe_load(f)

    for key, value in languages["eng"].items():
        languages[lang].setdefault(key, value)

    try:
        languages_present[lang] = languages[lang]["name"]
    except KeyError:
        print(
            "Language file error detected. "
            "Please report it to @ArchAssociation on Telegram"
        )
        sys.exit(1)