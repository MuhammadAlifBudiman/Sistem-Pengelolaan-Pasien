class Pagination:
    """
    A class representing pagination information.

    Attributes:
        current_page (int): The current page number.
        size_page (int): The number of items per page.
        max_page (int): The maximum number of pages.
        total_data (int): The total number of data items.
    """

    def __init__(self, current_page: int, size_page: int, max_page: int, total_data: int):
        self.current_page = current_page
        self.size_page = size_page
        self.max_page = max_page
        self.total_data = total_data

class DatatablesPagination:
    """
    Represents pagination information for Datatables.

    Args:
        recordsTotal (int): The total number of records in the dataset.
        recordsFiltered (int): The number of records after filtering.
        draw (int, optional): The draw counter. Defaults to None.
        start (int, optional): The starting index of the records. Defaults to None.
        length (int, optional): The number of records to be displayed. Defaults to None.
    """

    def __init__(self, recordsTotal: int, recordsFiltered: int, draw: int = None, start: int = None, length: int = None):
        self.draw = draw
        self.start = start
        self.length = length
        self.recordsTotal = recordsTotal
        self.recordsFiltered = recordsFiltered