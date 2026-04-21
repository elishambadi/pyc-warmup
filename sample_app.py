import json
import re
from html import escape
from typing import Optional

def extract_json_payload(text: str) -> str:
    stripped = text.strip()
    fenced_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.IGNORECASE | re.DOTALL)
    print(f"Extracting JSON payload from text. Fenced match found: {bool(fenced_match)}")
    if fenced_match:
        fenced_result = fenced_match.group(1).strip()
        print(f"Fenced match content:\n{fenced_result}\n")
        return fenced_result

    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace:last_brace + 1]

    return stripped

if __name__ == "__main__":
    raw_json = """
    ```json
    {
    "title": "The Complete 10-Minute Warm-Up Routine for Choir Rehearsal",
    "category": "warmup",
    "excerpt": "<p>A great warm-up sets the foundation for productive rehearsal and protects your voice. Learn a simple, science-backed routine that prepares your body, breath, and voice in just 10 minutes—whether you're a soloist getting ready or a section leader preparing your group.</p>",
    "body": "<h2>Why Warming Up Matters</h2><p>Think of your voice like any other muscle. You wouldn't sprint without stretching, and you shouldn't sing at full power without preparation. A proper warm-up increases blood flow to your vocal cords, loosens tension in your neck and shoulders, establishes consistent breath support, and helps you find your best tone right from the start of rehearsal.</p><p>Beyond the physical benefits, warming up mentally prepares you to be present, focused, and ready to tackle challenging repertoire. It's an investment that pays dividends in every rehearsal.</p><h2>The Complete 10-Minute Routine</h2><h3>Minutes 1–2: Physical Release and Breathing</h3><p>Start by releasing tension. Roll your shoulders backward slowly, 5 times each direction. Gently roll your head in circles—but <strong>never straight back</strong>, as this can strain your neck. Drop your chin to your chest and hold for 10 seconds.</p><p>Now focus on breath awareness. Stand with feet hip-width apart. Breathe in through your nose for a count of 4, hold for 4, and exhale slowly through your mouth for 6 counts. Repeat 5 times. This calms your nervous system and anchors your diaphragm.</p><h3>Minutes 3–4: Lip Trills and Sirens</h3><p>Lip trills (also called \\"raspberry sounds\\") are magical for warming up the vocal cords without strain. Take a comfortable breath and blow air through closed lips while making a motorboat sound. Let your voice float over the sound—no pressure, just flow.</p>"
    }
    ```
    """

    print("Extracting JSON payload...")
    print("Raw input:")
    print(raw_json)
    print("-" * 40)
    payload = extract_json_payload(raw_json)
    try:
        data = json.loads(payload)
        print("Extracted data:")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print("Raw payload:")