from rest_framework.pagination import PageNumberPagination
from django.conf import settings

class SmartPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200

    def paginate_queryset(self, queryset, request, view=None):
        # Bypass pagination pour tests/benchmarks
        bypass = getattr(settings, 'DISABLE_PAGINATION', False) or \
                 request.headers.get('X-Bypass-Pagination') == '1'
        if bypass:
            return None  # DRF renverra une liste non paginée
        return super().paginate_queryset(queryset, request, view)
