class EventRequest:
    CREATE_RECIPE = "CREATE_RECIPE"
    STOP_RECIPE = "STOP_RECIPE"
    LOAD_CONFIG = "LOAD_CONFIG"


class EventResponse:
    INVALID_REQUEST = "Invalid Request"
    INVALID_EVENT = "Invalid Event"
    SUCCESS = "Success"