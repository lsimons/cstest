[include "license.tpl"]
from .base import Struct


class [model_name](Struct):
    def __init__(self, **kwargs):[for fields]
        """
        [fields.desc] [is fields.pythonType ""][else]
        :type: [fields.pythonType][end]
        """
        self.[fields.name] = None[end]

        super([model_name], self).__init__(**kwargs)
