"""Pagination for the menu API."""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Page-number pagination that lets the client request a larger page via
    ?page_size= (e.g. the storefront menu grid fetches all items at once),
    while keeping a sane default and a hard maximum.
    """

    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 200
