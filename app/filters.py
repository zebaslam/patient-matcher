import re
import base64


def camel_to_title(text):
    """Convert camelCase or snake_case to Title Case with spaces."""
    # Replace underscores with spaces
    text = text.replace("_", " ")
    # Insert space before uppercase letters (except the first one)
    text = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    # Capitalize first letter of each word
    return text.title()


def jinja_attribute(obj, name, default=None):
    """Jinja filter to get an attribute by name, with optional default."""
    return getattr(obj, name, default)


def b64encode_filter(s):
    """Jinja filter to base64 encode a string."""
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode("utf-8")


def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters["camel_to_title"] = camel_to_title
    app.jinja_env.filters["attribute"] = jinja_attribute
    app.jinja_env.filters["b64encode"] = b64encode_filter
    # Add more filters here as needed
