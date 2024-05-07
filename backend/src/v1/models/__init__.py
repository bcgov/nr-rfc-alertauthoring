# from .model import User, UserAddress
import logging

import sqlmodel

LOGGER = logging.getLogger(__name__)


def get_subclasses(cls):
    for subclass in cls.__subclasses__():
        LOGGER.debug(f"subclass: {subclass}")
        yield from get_subclasses(subclass)
        yield subclass

models_dict = {cls.__name__: cls for cls in get_subclasses(sqlmodel.SQLModel)}   

for cls in models_dict.values():
    LOGGER.debug(f"class: {cls}")
    cls.update_forward_refs(**models_dict)



