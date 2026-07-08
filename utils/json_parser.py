import json
import re

def parse_json_response(text):
    text = text.strip()
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```python", "", text)
    text = re.sub(r"```", "", text).strip()

    start = text.find("{")
    if start == -1:
        return {"raw_response": text}

    brace_count = 0
    end = -1

    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1

        if brace_count == 0:
            end = i + 1
            break

    if end == -1:
        return {"raw_response": text}

    try:
        return json.loads(text[start:end])
    except Exception:
        return {"raw_response": text}