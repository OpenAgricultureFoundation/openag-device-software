class RecipeError(Exception):
    """Base class for recipe errors."""
    ...


class InvalidTransitionModeError(RecipeError):
    ...


class InvalidUUIDError(RecipeError):
    ...
