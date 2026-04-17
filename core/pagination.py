from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class LogPagination(PageNumberPagination):
    page_size = 50  # logs usually need larger pages
    page_size_query_param = "page_size"
    max_page_size = 200