class EventRequest:
    LOAD_RECIPE = "Load Recipe"
    STOP_RECIPE = "Stop Recipe"
    LOAD_CONFIG = "Load Config"


class EventResponse:
    INVALID_REQUEST = "Invalid Request"
    INVALID_EVENT = "Invalid Event"
    SUCCESS = "Success"