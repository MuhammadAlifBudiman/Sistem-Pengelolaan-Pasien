# pagination.py
# This module provides classes for handling pagination logic and metadata, including a general Pagination class and a Datatables-specific pagination class.

class Pagination:
    """
    A class representing pagination information for general use.

    Attributes:
        current_page (int): The current page number (1-based index).
        size_page (int): The number of items per page.
        max_page (int): The maximum number of pages available.
        total_data (int): The total number of data items across all pages.
    """

    def __init__(self, current_page: int, size_page: int, max_page: int, total_data: int):
        """
        Initialize a Pagination object.

        Args:
            current_page (int): The current page number (1-based index).
            size_page (int): The number of items per page.
            max_page (int): The maximum number of pages available.
            total_data (int): The total number of data items.
        """
        self.current_page = current_page  # The current page number
        self.size_page = size_page        # The number of items per page
        self.max_page = max_page          # The maximum number of pages
        self.total_data = total_data      # The total number of data items


class DatatablesPagination:
    """
    Represents pagination information for Datatables (commonly used in web data tables).

    Attributes:
        recordsTotal (int): The total number of records in the dataset (before filtering).
        recordsFiltered (int): The number of records after filtering (search, etc.).
        draw (int, optional): The draw counter for Datatables requests (used for synchronization).
        start (int, optional): The starting index of the records for the current page.
        length (int, optional): The number of records to be displayed per page.
    """

    def __init__(self, recordsTotal: int, recordsFiltered: int, draw: int = None, start: int = None, length: int = None):
        """
        Initialize a DatatablesPagination object.

        Args:
            recordsTotal (int): The total number of records in the dataset.
            recordsFiltered (int): The number of records after filtering.
            draw (int, optional): The draw counter for Datatables requests. Defaults to None.
            start (int, optional): The starting index of the records. Defaults to None.
            length (int, optional): The number of records to be displayed. Defaults to None.
        """
        self.draw = draw                  # Draw counter for Datatables (request synchronization)
        self.start = start                # Starting index for the current page
        self.length = length              # Number of records per page
        self.recordsTotal = recordsTotal  # Total records before filtering
        self.recordsFiltered = recordsFiltered  # Records after filtering
