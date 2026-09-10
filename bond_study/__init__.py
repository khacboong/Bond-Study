"""Bond Study application package."""


def main():
    """Start the app lazily without importing the full Qt UI on package import."""
    from .app import main as run_app

    return run_app()


__all__ = ["main"]
