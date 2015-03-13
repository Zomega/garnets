class UnhandledEventException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "A Widget Encountered an Unhandled Event"
