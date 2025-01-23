from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """
    Пагинация для курсов
    """
    page_size = 5  # Количество элементов на одной странице
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы через запрос
    max_page_size = 20  # Максимальное количество элементов на странице


class LessonPagination(PageNumberPagination):
    """
    Пагинация для уроков
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
