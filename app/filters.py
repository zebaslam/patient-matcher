import re


def camel_to_title(text):
    """Convert camelCase to Title Case with spaces."""
    # Insert space before uppercase letters (except the first one)
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    # Capitalize first letter of each word
    return result.title()


def jinja_attribute(obj, name, default=None):
    """Jinja filter to get an attribute by name, with optional default."""
    return getattr(obj, name, default)


def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters["camel_to_title"] = camel_to_title
    app.jinja_env.filters["attribute"] = jinja_attribute
    # Add more filters here as needed
