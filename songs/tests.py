from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase

from .musicxml import extract_voicenotes_from_musicxml


class MusicXMLExtractionTests(TestCase):
		def test_extracts_parts_notes_and_lyrics(self):
				xml_content = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<score-partwise version=\"3.1\">
	<part-list>
		<score-part id=\"P1\"><part-name>Soprano</part-name></score-part>
		<score-part id=\"P2\"><part-name>Alto</part-name></score-part>
	</part-list>
	<part id=\"P1\">
		<measure number=\"1\">
			<attributes><divisions>4</divisions></attributes>
			<note>
				<pitch><step>C</step><octave>4</octave></pitch>
				<duration>4</duration>
				<lyric><text>La</text></lyric>
			</note>
			<note>
				<rest/>
				<duration>4</duration>
			</note>
		</measure>
	</part>
	<part id=\"P2\">
		<measure number=\"1\">
			<attributes><divisions>4</divisions></attributes>
			<note>
				<pitch><step>E</step><alter>-1</alter><octave>4</octave></pitch>
				<duration>8</duration>
			</note>
		</measure>
	</part>
</score-partwise>
"""

				with TemporaryDirectory() as temp_dir:
						xml_path = Path(temp_dir) / "sample.musicxml"
						xml_path.write_text(xml_content, encoding="utf-8")
						result = extract_voicenotes_from_musicxml(xml_path)

				self.assertIn("Soprano", result)
				self.assertIn("Alto", result)
				self.assertEqual(len(result["Soprano"]), 2)
				self.assertEqual(len(result["Alto"]), 1)

				first_soprano_note = result["Soprano"][0]
				self.assertFalse(first_soprano_note.is_rest)
				self.assertEqual(first_soprano_note.lyric, "La")
				self.assertEqual(first_soprano_note.measure, 1)
				self.assertAlmostEqual(first_soprano_note.duration_quarter, 1.0)
				self.assertEqual(first_soprano_note.midi, 60)

				second_soprano_note = result["Soprano"][1]
				self.assertTrue(second_soprano_note.is_rest)

				alto_note = result["Alto"][0]
				self.assertEqual(alto_note.step, "E")
				self.assertEqual(alto_note.alter, -1)
				self.assertEqual(alto_note.midi, 63)


class SongRequestTests(TestCase):
    def post_request(self, **overrides):
        data = {
            'song_title': 'Way Maker',
            'artist': 'Sinach',
            'request_type': 'both',
            'voice_part': 'Soprano',
            'details': 'The live version please.',
            'requester_name': 'Ada',
            'requester_email': 'ada@example.com',
        }
        data.update(overrides)
        return self.client.post(
            '/request-song/',
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_ACCEPT='application/json',
        )

    def test_valid_request_is_stored_and_sent(self):
        from unittest.mock import patch
        from .models import SongRequest

        with patch('songs.views.send_song_request', return_value=(True, '')) as sender:
            response = self.post_request()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        song_request = SongRequest.objects.get()
        self.assertEqual(song_request.song_title, 'Way Maker')
        self.assertTrue(song_request.discord_sent)
        sender.assert_called_once_with(song_request)

    def test_missing_title_is_rejected(self):
        from .models import SongRequest

        response = self.post_request(song_title='')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('song_title', response.json()['errors'])
        self.assertFalse(SongRequest.objects.exists())

    def test_honeypot_submission_is_ignored(self):
        from .models import SongRequest

        response = self.post_request(website='https://spam.example')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertFalse(SongRequest.objects.exists())

    def test_get_is_not_allowed(self):
        response = self.client.get('/request-song/')

        self.assertEqual(response.status_code, 405)

    def test_discord_payload_has_no_mention_pings(self):
        from .discord import build_song_request_payload
        from .models import SongRequest

        song_request = SongRequest.objects.create(
            song_title='Test @everyone',
            request_type='lyrics',
        )
        payload = build_song_request_payload(song_request)

        self.assertEqual(payload['allowed_mentions'], {'parse': []})
        self.assertEqual(payload['embeds'][0]['title'], '🎵 New song request')
