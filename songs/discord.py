"""Delivery of song requests to a Discord channel webhook."""

import json
import logging
from urllib import error, request as urllib_request

from django.conf import settings

logger = logging.getLogger(__name__)

EMBED_COLOR = 0x4B3FA0
FIELD_VALUE_LIMIT = 1024
REQUEST_TIMEOUT_SECONDS = 8


def _truncate(value, limit=FIELD_VALUE_LIMIT):
    value = (value or '').strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + '…'


def _embed_field(name, value, inline=True):
    """Return a Discord embed field, or None when there is nothing to show."""
    value = _truncate(value)
    if not value:
        return None
    return {'name': name, 'value': value, 'inline': inline}


def build_song_request_payload(song_request):
    """Build the JSON body for a Discord webhook message."""
    fields = [
        _embed_field('Song', song_request.song_title),
        _embed_field('Artist / composer', song_request.artist),
        _embed_field('Requested', song_request.get_request_type_display()),
        _embed_field('Voice part', song_request.voice_part),
    ]

    if song_request.details:
        fields.append(_embed_field('Details', song_request.details, inline=False))

    requester = song_request.requester_name or 'Anonymous'
    if song_request.requester_email:
        requester = f"{requester}\n{song_request.requester_email}"
    fields.append(_embed_field('Requested by', requester, inline=False))

    embed = {
        'title': '🎵 New song request',
        'color': EMBED_COLOR,
        'fields': [field for field in fields if field],
        'footer': {'text': 'PYC WarmUp  •  Song requests'},
        'timestamp': song_request.created_at.isoformat(),
    }

    return {
        'username': 'PYC WarmUp Requests',
        'embeds': [embed],
        # Never let visitor-supplied text ping @everyone/@here or roles.
        'allowed_mentions': {'parse': []},
    }


def send_song_request(song_request, webhook_url=None):
    """
    POST a song request to Discord.

    Returns ``(sent, error_message)``. Deliberately never raises: the request
    is always stored locally, so a Discord outage must not lose it.
    """
    url = webhook_url or getattr(settings, 'DISCORD_WEBHOOK_URL', '')
    if not url:
        message = 'Discord webhook is not configured (set DISCORD_WEBHOOK_URL).'
        logger.warning(message)
        return False, message

    body = json.dumps(build_song_request_payload(song_request)).encode('utf-8')
    http_request = urllib_request.Request(
        url,
        data=body,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'PYC-WarmUp/1.0 (+https://pyc.elimbadi.com)',
        },
        method='POST',
    )

    try:
        with urllib_request.urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status = getattr(response, 'status', response.getcode())
            if 200 <= status < 300:
                return True, ''
            return False, f'Discord returned HTTP {status}.'
    except error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:300]
        message = f'Discord returned HTTP {exc.code}: {detail}'
        logger.warning('Discord webhook rejected song request %s: %s', song_request.pk, message)
        return False, message
    except error.URLError as exc:
        message = f'Could not reach Discord: {exc.reason}'
        logger.warning('Discord webhook unreachable for song request %s: %s', song_request.pk, message)
        return False, message
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception('Unexpected error sending song request %s to Discord', song_request.pk)
        return False, str(exc)
