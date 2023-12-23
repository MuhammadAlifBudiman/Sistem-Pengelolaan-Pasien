class Pagination:
    def __init__(self, current_page: int, size_page: int, max_page: int, total_data: int):
        self.current_page = current_page
        self.size_page = size_page
        self.max_page = max_page
        self.total_data = total_data

class DatatablesPagination:
    def __init__(self, recordsTotal: int, recordsFiltered: int, draw: int = None, start: int = None, length: int = None,):
        self.draw = draw
        self.start = start
        self.length = length
        self.recordsTotal = recordsTotal
        self.recordsFiltered = recordsFiltered