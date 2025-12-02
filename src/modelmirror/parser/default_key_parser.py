from modelmirror.parser.code_link_parser import CodeLinkParser


class DefaultCodeLinkParser(CodeLinkParser):
    def __init__(self, placeholder: str = "$mirror"):
        super().__init__(placeholder)
