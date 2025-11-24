from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar que permite cambiar el tamaño de página mediante el parámetro `page_size`.

    Usar este paginador en ViewSets que necesiten soporte de `?page_size=` desde el cliente.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
