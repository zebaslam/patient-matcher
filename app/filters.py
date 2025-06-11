import re


def camel_to_title(text):
    """Convert camelCase to Title Case with spaces."""
    # Insert space before uppercase letters (except the first one)
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    # Capitalize first letter of each word
    return result.title()


def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters["camel_to_title"] = camel_to_title
    # Add more filters here as needed
