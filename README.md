# Congressional App Challenge Submission

This is our submission to the congressional app challenge. Quick Fill is a chrome extension that allows a user to expedite their writing processes. When a hotkey is pressed, the extension will query the Docs API and
retrieve the user's document text. It will then summarize this text using the Hugging Face pipeline and query GPT-3. Then, the Docs API will output this response on the user's screen as light-grey italic text. The user can 
confirm that this is indeed the text they want by pressing the hot key once again, which will change the text to a style following the preceding text. Below are genral explinations for what each file does. Feel free
to reach out with any questions or advice if you're working on something similar!

## docs/docs.py
The docs.py file is responsible for interacting with the Google Docs API to manipulate the content of Google Documents programmatically. It includes functions to:

- Fetch and Read Document Content: The script can retrieve the content of a Google Doc, including paragraphs, tables, and other structural elements, and compile it into plain text.
- Modify Document Content: It allows for various modifications to the document's content, such as inserting new text, deleting specified text ranges, and updating the style of specific text ranges (e.g., changing the color or making text italicized).
- Google Docs API Integration: The script manages the integration with Google Docs API, handling authentication and executing requests to read or update document content.

## docs/docs_blueprint.py
The docs_blueprint.py file manages the authentication process for accessing Google Docs via OAuth 2.0 within a Flask application. It includes the following key functionalities:

- OAuth 2.0 Authentication: This script handles the OAuth 2.0 authentication flow, enabling users to log in with their Google accounts. It redirects users to the Google authorization page and handles the callback to retrieve the authentication token.
- Session Management: The script manages user sessions, storing the user's Google ID and name in the session after successful authentication. It also includes a route for logging out and clearing the session.
- Access Control: It includes a decorator function auth_required to restrict access to certain routes, ensuring that only authenticated users can access them.
- CORS and Secure Development: The script allows Cross-Origin Resource Sharing (CORS) and bypasses the HTTPS requirement for OAuth 2.0, making it suitable for development environments.

## server.py

The server.py file is the main entry point for the Flask application, which serves as the backend for handling requests related to the Google Docs integration and the autocomplete functionality. It includes the following key features:

- Flask Application Setup: The script initializes a Flask application, registers the docs_blueprint for handling Google Docs authentication, and sets a secret key for session management.
- Global State Management: It manages global variables (document_start_index and document_end_index) to keep track of where the autocomplete text is inserted in the Google Doc.
- API Endpoints:
    * /api/preview-autocomplete: This endpoint previews the autocomplete suggestion by inserting placeholder text into the Google Doc at the current cursor position. It also applies a temporary style (e.g., italicized and gray text) to the inserted text to distinguish it as a suggestion.
    * /api/confirm-autocomplete: This endpoint confirms the autocomplete suggestion by finalizing the inserted text and removing the temporary styling, making it appear as normal text in the document.
- Google Docs API Integration: The script fetches and modifies the content of Google Docs by interacting with the Google Docs API, using the authenticated user's credentials.
- Authentication Requirement: Both API endpoints require the user to be authenticated via OAuth 2.0, ensuring that only authorized users can modify Google Docs.
