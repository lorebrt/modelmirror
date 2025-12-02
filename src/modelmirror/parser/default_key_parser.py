from modelmirror.parser.code_link_parser import CodeLinkParser, FormatValidation, ParsedKey


class DefaultCodeLinkParser(CodeLinkParser):
    def __init__(self, placeholder: str = "$mirror"):
        super().__init__(placeholder)

    def _validate(self, key: str) -> FormatValidation:
        return FormatValidation(is_valid=True)

    def _parse(self, key: str) -> ParsedKey:
        if ":" in key:
            id, instance = key.split(":", 1)
            return ParsedKey(id=id, instance=instance)
        return ParsedKey(id=key, instance=None)
