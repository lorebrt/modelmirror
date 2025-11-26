from modelmirror.parser.reference_parser import FormatValidation, ParsedReference, ReferenceParser


class DefaultReferenceParser(ReferenceParser):
    def _validate(self, reference: str) -> FormatValidation:
        return FormatValidation(is_valid=True)

    def _parse(self, reference: str) -> ParsedReference:
        if ":" in reference:
            id, instance = reference.split(":", 1)
            return ParsedReference(id=id, instance=instance)
        return ParsedReference(id=reference, instance=None)
