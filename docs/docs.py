from dataclasses import dataclass
from typing import Any, Union, Optional, Dict

# noinspection PyPackageRequirements
import google.oauth2.credentials

# noinspection PyPackageRequirements
import googleapiclient

# noinspection PyPackageRequirements
from googleapiclient.discovery import build

# noinspection PyPackageRequirements
from googleapiclient.errors import HttpError


class __DocumentBodyReader:
    """A class that houses function that help read the body of a Google Doc.

    The Google Docs API returns a large, nested JSON response when attempting to
    get the body of a Google Doc. This class houses functions that help with
    traversing that JSON response.
    """

    @staticmethod
    def __read_paragraph_element(element):
        text_run = element.get("textRun")
        if not text_run:
            return ""
        return text_run.get("content")

    def read_structural_elements(self, elements):
        text = ""
        for value in elements:
            if "paragraph" in value:
                elements = value.get("paragraph").get("elements")
                for elem in elements:
                    text += self.__read_paragraph_element(elem)
            elif "table" in value:
                table = value.get("table")
                for row in table.get("tableRows"):
                    cells = row.get("tableCells")
                    for cell in cells:
                        text += self.read_structural_elements(
                            cell.get("content"))
            elif "tableOfContents" in value:
                toc = value.get("tableOfContents")
                text += self.read_structural_elements(toc.get("content"))
        return text


def fetch_service(
    credentials: google.oauth2.credentials.Credentials,
) -> googleapiclient.discovery.Resource:
    """Gets an instance of a Google Docs service object.

    :param credentials: The credentials provided by authorization.

    :return: The Google Docs service object.
    """
    try:
        service = build("docs", "v1", credentials=credentials)
        return service
    except HttpError:
        print(HttpError)


def fetch_document(service: googleapiclient.discovery.Resource,
                   document_id: str) -> Union[Dict[str, Any], dict]:
    """Fetches information about a Google Doc.

    :param service: The Google Docs service object.
    :param document_id: A forty-four character ID that corresponds to a valid
        Google Doc.

    :return: A dictionary containing the ID, title, and body of the Google Doc.
    """
    try:
        document = service.documents().get(documentId=document_id).execute()

        document_body = __DocumentBodyReader().read_structural_elements(
            document.get("body").get("content"))
        characters = len(document_body.replace("\n", " "))
        words = len([
            word for word in document_body.replace("\n", " ").split(" ")
            if word
        ])

        return {
            "id": document.get("documentId"),
            "title": document.get("title"),
            "body": document_body,
            "characters": characters,
            "words": words,
        }
    except HttpError:
        return dict()


@dataclass
class Range:
    start_index: int
    end_index: Optional[int] = None


@dataclass
class Color:
    blue: Optional[float] = 0
    green: Optional[float] = 0
    red: Optional[float] = 0


@dataclass
class TextStyle:
    italic: Optional[bool] = False
    color: Optional[Color] = Color()


class DocumentRequests:
    """A class for creating requests sent to the Google Docs Resource."""

    def __init__(self):
        self.requests = []

    def insert_text(self, document_range: Range, text: str) -> None:
        """Adds an `insertText` request to the requests attribute.

        The `insertText` request inserts text in the Google Doc at a specified
        range start index. The range only requires a start index and not an end
        index.

        :param document_range: A `Range` object that indicates where the text
            should be inserted.
        :param text: The text that will be inserted.
        """
        self.requests.append({
            "insertText": {
                "location": {
                    "index": document_range.start_index
                },
                "text": text,
            }
        })

    def delete_content_range(self, document_range: Range) -> None:
        """Adds a `deleteContentRange` request to the requests attribute.

        The `deleteContentRange` request deletes a range of text in the Google
        Doc. The range requires both a start and end index.

        :param document_range: A `Range` object that indicates the range where
            content should be deleted.
        """
        self.requests.append({
            "deleteContentRange": {
                "range": {
                    "startIndex": document_range.start_index,
                    "endIndex": document_range.end_index,
                }
            }
        })

    def update_text_style(self, document_range: Range,
                          text_style: TextStyle) -> None:
        """Adds an `updateTextStyle` request to the requests attribute.

        The `updateTextStyle` requests changes the style of text within a
        particular range in the Google Doc. The range requires both a start and
        end index. While the `updateTextStyle` request changes many properties
        of the text, this function can only change the color and foreground
        color of the text.

        :param document_range: A `Range` object that indicates the range where
            the text style should be updated.
        :param text_style: A `TextStyle` object that indicates the style to
            which the text should be updated.
        """
        self.requests.append({
            "updateTextStyle": {
                "range": {
                    "startIndex": document_range.start_index,
                    "endIndex": document_range.end_index,
                },
                "textStyle": {
                    "italic": text_style.italic,
                    "foregroundColor": {
                        "color": {
                            "rgbColor": {
                                "blue": text_style.color.blue,
                                "green": text_style.color.green,
                                "red": text_style.color.red,
                            }
                        }
                    },
                },
                "fields": "italic,foregroundColor",
            }
        })


def modify_document_body(
    service: googleapiclient.discovery.Resource,
    document_id: str,
    document_requests: DocumentRequests,
) -> None:
    """Sends text requests to the Google Docs Resource.

    :param service: The Google Docs service object.
    :param document_id: A forty-four character ID that corresponds to a valid
        Google Doc.
    :param document_requests: A `DocumentRequests` object.
    """
    service.documents().batchUpdate(documentId=document_id,
                                    body={
                                        "requests": document_requests.requests
                                    }).execute()
