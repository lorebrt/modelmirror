"""
FastAPI class registers.
"""

from modelmirror.class_provider.class_reference import ClassReference
from modelmirror.class_provider.class_register import ClassRegister

try:
    from fastapi import FastAPI

    class FastAPIRegister(ClassRegister):
        reference = ClassReference(id="fastapi_app", cls=FastAPI)

except ImportError:
    pass
