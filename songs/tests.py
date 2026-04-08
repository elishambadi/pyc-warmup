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
