from modelmirror.parser.key_parser import FormatValidation, KeyParser, ParsedKey


class DefaultKeyParser(KeyParser):
    def __init__(self, placeholder: str = "$mirror"):
        super().__init__(placeholder)

    def _validate(self, key: str) -> FormatValidation:
        return FormatValidation(is_valid=True)

    def _parse(self, key: str) -> ParsedKey:
        if ":" in key:
            id, instance = key.split(":", 1)
            return ParsedKey(id=id, instance=instance)
        return ParsedKey(id=key, instance=None)
