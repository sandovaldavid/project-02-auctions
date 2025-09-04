from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that allows clients to specify page size via URL parameter.
    """

    page_size = 20  # Default page size
    page_size_query_param = "page_size"  # Allow client to override page size
    max_page_size = 100  # Maximum allowed page size
    page_query_param = "page"  # Page number parameter name
