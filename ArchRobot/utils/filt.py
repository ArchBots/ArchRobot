import re
from typing import List, Tuple, Optional


TELEGRAM_CMD_MAX_LENGTH = 31


def _parse_single(part: str) -> Tuple[str, str, List[str]]:
    part = part.strip()
    if part.startswith('"') and part.endswith('"'):
        phrase = part[1:-1]
        return (phrase, phrase.lower(), [])
    if part.startswith("prefix:"):
        word = part[7:]
        return (word, word.lower(), ["prefix"])
    if part.startswith("exact:"):
        word = part[6:]
        return (word, word.lower(), ["exact"])
    return (part, part.lower(), [])


def parse_trigger(trigger_str: str) -> List[Tuple[str, str, List[str]]]:
    trigger_str = trigger_str.strip()

    if trigger_str.startswith("(") and trigger_str.endswith(")"):
        parts = []
        current = []
        in_quotes = False

        for char in trigger_str[1:-1]:
            if char == '"':
                in_quotes = not in_quotes
            elif char == "," and not in_quotes:
                if current:
                    parts.append("".join(current).strip())
                current = []
                continue
            current.append(char)

        if current:
            parts.append("".join(current).strip())

        return [_parse_single(p) for p in parts if p]

    return [_parse_single(trigger_str)]


def expand_fillings(text: str, user_name: str, admin_name: Optional[str] = None, replytag_user: Optional[str] = None) -> str:
    text = text.replace("{user}", user_name)
    if admin_name:
        text = text.replace("{admin}", admin_name)
    if replytag_user:
        text = text.replace("{replytag}", replytag_user)
    return text


def has_filling(text: str, filling: str) -> bool:
    return filling in text


def expand_command_filling(text: str) -> str:
    pattern = r'\{command\}/([a-z0-9_]{1,' + str(TELEGRAM_CMD_MAX_LENGTH) + r'})'
    return re.sub(pattern, r'/\1', text)