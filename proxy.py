# for blocking particular keywords in URL

from mitmproxy import http
from urllib.parse import urlparse, parse_qs

class InterceptURLs:
    # Define common search query parameters
    search_query_params = ["q", "query", "search"]

    def __init__(self, blocked_keywords):
        # Initialize with a list of blocked keywords (case-insensitive)
        self.blocked_keywords = [keyword.lower() for keyword in blocked_keywords]

    def request(self, flow: http.HTTPFlow):
        # Get the full URL from the request
        url = flow.request.pretty_url

        # Parse the URL to extract components
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Convert netloc and path to lowercase for case-insensitive matching
        netloc_and_path_lower = (parsed_url.netloc + parsed_url.path).lower()

        # Check if the URL contains any of the blocked keywords (case-insensitive)
        contains_blocked_keyword = any(keyword in netloc_and_path_lower for keyword in self.blocked_keywords)

        # Check if the URL contains common search parameters
        is_search_query = any(param in query_params for param in self.search_query_params)

        # Block the URL if it contains blocked keywords and is not a search query
        if contains_blocked_keyword and not is_search_query:
            # Respond with a custom error message (e.g., 403 Forbidden)
            flow.response = http.Response.make(
                403,  # Status code for Forbidden
                b"Access to this website is blocked due to restricted content.",  # Custom message
                {"Content-Type": "text/html"}  # Headers
            )
            print(f"Blocked access to: {url}")
        else:
            # Allow the request to proceed
            print(f"Connecting to: {url}")

# Prompt the user for blocked keywords input
blocked_keywords_input = input("Enter blocked keywords, separated by commas: ")
blocked_keywords = [keyword.strip() for keyword in blocked_keywords_input.split(",")]

# Initialize the addon with user-provided blocked keywords
addons = [
    InterceptURLs(blocked_keywords)
]
