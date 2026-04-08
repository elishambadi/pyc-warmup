from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union
import xml.etree.ElementTree as ET


@dataclass
class ExtractedNote:
    measure: int
    beat: float
    duration_divisions: int
    duration_quarter: float
    step: Optional[str]
    alter: int
    octave: Optional[int]
    midi: Optional[int]
    is_rest: bool
    lyric: Optional[str]


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _find_child(element: ET.Element, name: str) -> Optional[ET.Element]:
    for child in list(element):
        if _strip_namespace(child.tag) == name:
            return child
    return None


def _find_children(element: ET.Element, name: str) -> List[ET.Element]:
    return [child for child in list(element) if _strip_namespace(child.tag) == name]


def _safe_int(value: Optional[str], default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _safe_float(value: Optional[str], default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


STEP_TO_SEMITONE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}


def _pitch_to_midi(step: Optional[str], alter: int, octave: Optional[int]) -> Optional[int]:
    if not step or octave is None:
        return None
    base = STEP_TO_SEMITONE.get(step.upper())
    if base is None:
        return None
    return (octave + 1) * 12 + base + alter


def extract_voicenotes_from_musicxml(source: Union[str, Path]) -> Dict[str, List[ExtractedNote]]:
    path = Path(source)
    tree = ET.parse(path)
    root = tree.getroot()

    part_name_by_id: Dict[str, str] = {}
    part_list = _find_child(root, "part-list")
    if part_list is not None:
        for score_part in _find_children(part_list, "score-part"):
            part_id = score_part.attrib.get("id", "")
            part_name_el = _find_child(score_part, "part-name")
            part_name = (part_name_el.text or "").strip() if part_name_el is not None else ""
            if part_id:
                part_name_by_id[part_id] = part_name or part_id

    extracted: Dict[str, List[ExtractedNote]] = {}

    for part in _find_children(root, "part"):
        part_id = part.attrib.get("id", "Unknown")
        voice_name = part_name_by_id.get(part_id, part_id)

        divisions = 1
        current_beat = 0.0
        voice_notes: List[ExtractedNote] = []

        for measure in _find_children(part, "measure"):
            measure_number = _safe_int(measure.attrib.get("number"), default=0)
            current_beat = 0.0

            attributes = _find_child(measure, "attributes")
            if attributes is not None:
                divisions_el = _find_child(attributes, "divisions")
                if divisions_el is not None:
                    divisions = max(_safe_int(divisions_el.text, default=1), 1)

            for note in _find_children(measure, "note"):
                duration_el = _find_child(note, "duration")
                duration_divisions = _safe_int(duration_el.text if duration_el is not None else None, default=0)
                duration_quarter = duration_divisions / divisions if divisions else 0.0

                rest_el = _find_child(note, "rest")
                is_rest = rest_el is not None

                step = None
                alter = 0
                octave = None
                midi = None

                if not is_rest:
                    pitch_el = _find_child(note, "pitch")
                    if pitch_el is not None:
                        step_el = _find_child(pitch_el, "step")
                        alter_el = _find_child(pitch_el, "alter")
                        octave_el = _find_child(pitch_el, "octave")
                        step = (step_el.text or "").strip() if step_el is not None else None
                        alter = _safe_int(alter_el.text if alter_el is not None else None, default=0)
                        octave = _safe_int(octave_el.text if octave_el is not None else None, default=-1)
                        if octave == -1:
                            octave = None
                        midi = _pitch_to_midi(step, alter, octave)

                lyric_text = None
                lyric_el = _find_child(note, "lyric")
                if lyric_el is not None:
                    text_el = _find_child(lyric_el, "text")
                    if text_el is not None and text_el.text:
                        lyric_text = text_el.text.strip()

                voice_notes.append(
                    ExtractedNote(
                        measure=measure_number,
                        beat=current_beat,
                        duration_divisions=duration_divisions,
                        duration_quarter=_safe_float(str(duration_quarter), 0.0),
                        step=step,
                        alter=alter,
                        octave=octave,
                        midi=midi,
                        is_rest=is_rest,
                        lyric=lyric_text,
                    )
                )

                current_beat += duration_quarter

        extracted[voice_name] = voice_notes

    return extracted
