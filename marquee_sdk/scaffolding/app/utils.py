from .data_loader           import data_loader
from hyperdrive2.models     import Publication

import json
import settings

def loadPublication():
    """
    Public: load the Publication specified in settings from the API

    Returns the active Publication
    """
    publication_container = data_loader.load(
        short_name=settings.PUBLICATION_SLUG    # TODO change from `short_name` to `slug`
    )
    return Publication(publication_container)

def getParam(req, param, default, validator):
    """
    Public: get a query parameter from the request, passing it through the
    given validator function.

    req         - The request.
    param       - The str name of the parameter to get
    default     - The default value if its not present or invalid
    validator   - The function to use to validate. MUST raise a ValueError if
                  the parameter value is invalid.
    """
    val = req.args.get(param, default)
    try:
        val = validator(val)
    except ValueError:
        val = default
    return val

def jsonResponse(data):
    return (json.dumps(data), 200, {'Content-Type': 'application/json'})
