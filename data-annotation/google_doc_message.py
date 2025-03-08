from html.parser import HTMLParser
from typing import override

import requests

class GoogleDocHTMLParser(HTMLParser):
    """A parser for Google Doc HTML data.

    Attributes:
        Public instance methods:
            __init__: Initialize superclass and subclass attributes.
            handle_starttag: Handle the start tag of an HTML element.
            handle_data: Process content of <span> HTML elements.

        Public instance variables:
            table_entries: The x-coordinates, y-coordinates, and Unicode
                characters that comprise the table data in the Google
                Doc HTML data.
    """

    @override
    def __init__(self) -> None:
        """Initialize a list for storing HTML table data."""
        super().__init__()
        self.table_entries = [[]]

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        """Store the start tag in a private instance attribute."""
        self._tag = tag

    @override
    def handle_data(self, data: str) -> None:
        """Process content of <span> HTML elements."""
        if self._tag == "span" and (data.isdigit() or not data.isascii()):
            data = int(data) if data.isdigit() else data
            self.table_entries[-1].append(data) if (
                len(self.table_entries[-1]) < 3) else (
                    self.table_entries.append([data]))

def print_google_doc_characters(url: str) -> None:
    """Print Unicode characters from Google Doc HTML input data.

    Fetch Google Doc HTML data from url, parse the HTML, and print
    Unicode characters that are stored as HTML table data to stdout at
    positions that correspond to the their x- and y-coordinates.

    Args:
        url: A Google Doc URL.

    Raises:
        requests.exceptions.HTTPError: An HTTP error occurred.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        parser = GoogleDocHTMLParser()
        parser.feed(response.text)
        sorted_entries = sorted(parser.table_entries,
                                key = lambda x: (x[-1], x[0]))
        sorted_entries = sorted(sorted_entries, key = lambda x: x[-1],
                                reverse = True)
        max_x = max(sorted_entries, key = lambda x: x[0])[0]
        message = ""
        x_coord = -1
        y_coord = sorted_entries[0][-1]
        for entry in sorted_entries:
            if entry[-1] != y_coord:
                y_coord = entry[-1]
                message += " " * (max_x - x_coord)
                message += "\n"
                x_coord = -1
            message += " " * (entry[0] - x_coord - 1) + entry[1]
            x_coord = entry[0]
        message += " " * (max_x - x_coord)
        print(message)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
