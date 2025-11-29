#src/utils/date_parser.py
import dateparser

def parse_natural_date(text: str) -> str | None:
    parsed = dateparser.parse(text)
    if not parsed:
        return None
    return parsed.strftime("%Y-%m-%d")
