import re


def snake_to_camel(string: str) -> str:
    return re.sub(r'_([a-zA-Z])', lambda match: match.group(1).upper(), string)


def camel_to_snake(string: str) -> str:
    result = re.sub(r'(?<!^)(?=[A-Z])', '_', string)
    return result.lower()
