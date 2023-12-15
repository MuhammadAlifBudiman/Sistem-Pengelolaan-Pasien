class Pagination:
    def __init__(self, current_page: int, size_page: int, max_page: int, total_data: int):
        self.current_page = current_page
        self.size_page = size_page
        self.max_page = max_page
        self.total_data = total_data


def paginate_data(data: list, page: int, per_page: int):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    return data[start_index:end_index]
