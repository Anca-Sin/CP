import json
from typing import Dict, Any

def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Clean and limit contact forms' inputs (prevents spam/abuse).

    Args:
        text: user input from contact forms
        max_length: max allowed characters (set to 2000 ~ 300-400 words)

    Returns:
        Cleaned text, truncated with "..." if msg exceeds 2k char.
    """
    cleaned = text.strip()

    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "..."

    # Removing null bytes that could cause issues
    cleaned = cleaned.replace("\x00", "")

    return cleaned


def create_cors_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates properly formatted API Gateway response with CORS headers.

    CORS = Cross-Origin Resource Sharing
    Same-origin Policy: browsers block requests between different domains for security.
    These headers tell the browser it's oki for any website to call my API.

    !!! In PROD replace * with actual domain for security !!!

    Args:
        status_code: HTTP code (200=success, 400=bad request, 500=server error)
        body: response data as Python dict (will be converted to JSON)

    Returns:
        Dictionary formatted in the way AWS API Gateway expects.
    """
    return {
        # Required struct for API Gateway response
        "statusCode": status_code, # HTTP response code

        "headers": {
            # Tells the browser what type of data I'm sending back
            "Content-Type": "application/json", # always JSON for APIs

            # The most important line - without this, the browser blocks everything!
            # * means any website can call me (change to https://bau.ranjdar-group.com)
            "Access-Control-Allow-Origin": "*",

            # Allow the browser to send certain headers in its request
            # Here Content-Type so the browser can tell it's sending JSON
            "Access-Control-Allow-Headers": "Content-Type",

            # Allow only specific HTTP methods
            # OPTIONS = browser check if it can call the API
            # POST = actual request - my contact form data submission
            "Access-Control-Allow-Methods": "OPTIONS, POST" # Don't need GET for project, will add later
        },

        # Convert Py dict to JSON str that browsers understand
        "body": json.dumps(body)
    }


def determine_language_from_domain(origin: str) -> str:
    """
    Determines which language to use based on subdomain.

    Args:
        origin: The origin header from API Gateway (ex. "https://bau.ranjdar-group.com")

    Returns:
        Language code: EN, DE, RO
    """
    # Extract subdomain from origin
    origin_lower = origin.lower()

    if "construction." in origin_lower: # can add or "retail" etc. in the future
        return "EN"

    elif "bau." in origin_lower:
        return "DE"

    elif "constructii." in origin_lower:
        return "RO"

    # Default to english for main domain or unknown subdomains
    return "EN"
