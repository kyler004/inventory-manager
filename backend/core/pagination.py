from rest_framework import PageNumberPagination
from rest_framework.response import Response

class StandardPagination(PageNumberPagination):
    """
    Implements the pagination from our API design
    { "status": "success", "data": [...], "meta": { ... } }
    """

    page_size = 20
    page_size = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'status' : 'success', 
            'data' : {
                'page': self.page.number, 
                'page_size': self.get_page_size(self.request), 
                'total_count': self.page.paginator.count, 
                'total_pages': self.page.paginator.num_pages, 
            }
        })