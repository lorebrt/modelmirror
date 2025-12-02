from modelmirror.parser.model_link import ModelLink
from modelmirror.parser.model_link_parser import ModelLinkParser


class DefaultModelLinkParser(ModelLinkParser):
    def parse(self, value: str) -> ModelLink | None:
        if isinstance(value, str) and value.startswith("$"):
            return ModelLink(id=value, instance=value)
        return None
