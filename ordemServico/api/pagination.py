from rest_framework.pagination import PageNumberPagination


class OptionalPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        should_paginate = any(
            request.query_params.get(param)
            for param in ('page', 'page_size', 'paginate')
        )
        if not should_paginate:
            return None
        return super().paginate_queryset(queryset, request, view=view)
