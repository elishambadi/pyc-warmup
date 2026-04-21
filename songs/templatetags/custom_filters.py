from django import template
from django.utils.html import strip_tags
import html
import re

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

@register.filter(name="is_admin")
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@register.filter
def get_voicenote(user_voicenotes, song_id):
    return user_voicenotes.filter(song__id=song_id).first()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to a Django form field.
    Usage: {{ form.my_field|add_class:"tailwind-classes-here" }}
    """
    return field.as_widget(attrs={"class": css_class})


@register.filter(name="html_to_text")
def html_to_text(value):
    if not value:
        return ""

    text = str(value)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)<li[^>]*>\s*", "\n• ", text)
    text = re.sub(r"(?is)</li>", "", text)
    text = re.sub(r"(?is)</(p|div|h[1-6]|ul|ol|blockquote|tr)>", "\n", text)

    text = strip_tags(text)
    text = html.unescape(text)

    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()