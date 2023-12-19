class Pagination:
    def __init__(self, current_page: int, size_page: int, max_page: int, total_data: int):
        self.current_page = current_page
        self.size_page = size_page
        self.max_page = max_page
        self.total_data = total_data

