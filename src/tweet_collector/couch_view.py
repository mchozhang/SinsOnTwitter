"""
A wrapper class for views in couchdb.
It will make writing views in python easier.
code from https://markhaa.se/couchdb-views-in-python.html
"""


from couchdb.design import ViewDefinition
import inflection
import sys


class CouchView(ViewDefinition):
    """
    A base class for couch views that handles the magic of instantiation.
    """

    def __init__(self):
        """
        Does some magic to map the subclass implementation into the format
        expected by ViewDefinition.
        """

        module = sys.modules[self.__module__]
        design_name = module.__name__.split('.')[-1]

        if hasattr(self.__class__, "map"):
            map_fun = self.__class__.map
        else:
            raise NotImplementedError("Couch views require a map() method.")

        if hasattr(self.__class__, "reduce"):
            reduce_fun = self.__class__.reduce
        else:
            reduce_fun = None

        super_args = (design_name,
                      inflection.underscore(self.__class__.__name__),
                      map_fun,
                      reduce_fun,
                      'python')

        super(CouchView, self).__init__(*super_args)
