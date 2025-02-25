from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)


@register.filter(name="youtube_embed")
def youtube_embed(value):
    """Replaces 'watch?v=' with 'embed/' in a YouTube URL"""
    if isinstance(value, str) and "watch?v=" in value:
        return value.replace("watch?v=", "embed/")
    return value