from flask import Flask, request
from http import HTTPStatus

from docs import *
from completion import completion
from response import response
from constants import *

app = Flask(__name__)
app.register_blueprint(docs_blueprint)
app.secret_key = "quickfill"

# Globals
document_start_index: int = None
document_end_index: int = None


@app.route("/api/preview-autocomplete", methods=["GET"])
@auth_required
def preview_autocomplete():
    document_id = request.args.get("document_id")
    if not document_id:
        return response(HTTPStatus.BAD_REQUEST,
                        error="The URL parameter `document_id` is not found.")

    docs_service = docs.fetch_service(docs_auth_flow.credentials)
    document_info = docs.fetch_document(docs_service, document_id)
    if not document_info:
        return response(
            HTTPStatus.BAD_REQUEST,
            error=
            ("The URL parameter `document_id` is either invalid or belongs to"
             " a document to which the authorized user does not have access."))

    global document_start_index
    document_start_index = document_info["characters"]

    # completion_service = completion.Completion(OPENAI_API_KEY)
    # autocomplete = " " + completion_service.fetch_autocomplete(
    #     document_info["body"])
    autocomplete = " This is some autocomplete text!"

    global document_end_index
    document_end_index = document_start_index + len(autocomplete)

    modification_requests = DocumentRequests()
    modification_requests.insert_text(Range(document_start_index), autocomplete)
    preview_text_style = TextStyle(italic=True, color=Color(0.5, 0.5, 0.5))
    modification_requests.update_text_style(
        Range(document_start_index, document_end_index), preview_text_style)

    docs.modify_document_body(docs_service, document_id, modification_requests)

    return response(
        HTTPStatus.OK,
        description="The document now contains the autocomplete text.")


@app.route("/api/confirm-autocomplete", methods=["GET"])
@auth_required
def confirm_autocomplete():
    document_id = request.args.get("document_id")
    if not document_id:
        return response(HTTPStatus.BAD_REQUEST,
                        error="The URL parameter `document_id` is not found.")

    docs_service = docs.fetch_service(docs_auth_flow.credentials)
    document_info = docs.fetch_document(docs_service, document_id)
    if not document_info:
        return response(
            HTTPStatus.BAD_REQUEST,
            error=
            ("The URL parameter `document_id` is either invalid or belongs to"
             " a document to which the authorized user does not have access."))

    global document_start_index, document_end_index

    confirm_text_style = TextStyle(italic=False)
    modification_requests = DocumentRequests()
    modification_requests.update_text_style(
        Range(document_start_index, document_end_index),
        confirm_text_style)

    modify_document_body(docs_service, document_id, modification_requests)

    document_start_index = document_end_index
    document_end_index = None

    return response(HTTPStatus.OK,
                    description="The autocomplete text has been confirmed.")


if __name__ == "__main__":
    app.run(debug=True)
