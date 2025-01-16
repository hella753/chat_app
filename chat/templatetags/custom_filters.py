from django import template

register = template.Library()

@register.filter
def get_extension(value):
    """
    Get the extension of a file.
    """
    return value.split(".")[-1].lower()