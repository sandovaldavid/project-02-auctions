# Mock django_heroku module for testing
# This prevents ImportError when running tests


def settings(locals_dict):
    """Mock function that does nothing"""
    pass
