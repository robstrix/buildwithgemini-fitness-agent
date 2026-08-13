# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
from google.adk.tools import ToolContext


def add(a: float, b: float) -> float:
    """Adds two numbers and returns the result.

    Args:
        a: First number.
        b: Second number.

    Returns:
        The sum of a and b.
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtracts the second number from the first number and returns the result.

    Args:
        a: First number (minuend).
        b: Second number (subtrahend).

    Returns:
        The difference (a - b).
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiplies two numbers and returns the result.

    Args:
        a: First number.
        b: Second number.

    Returns:
        The product of a and b.
    """
    return a * b


def divide(a: float, b: float) -> float:
    """Divides the first number by the second number and returns the result.

    Args:
        a: Dividend.
        b: Divisor.

    Returns:
        The quotient (a / b).
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def power(base: float, exponent: float) -> float:
    """Calculates the result of raising base to exponent.

    Args:
        base: The base number.
        exponent: The exponent power.

    Returns:
        base raised to exponent.
    """
    return math.pow(base, exponent)


def calculate_factorial(n: int) -> int:
    """Calculates the factorial of a non-negative integer n.

    Args:
        n: Non-negative integer.

    Returns:
        The factorial n!.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    return math.factorial(n)


FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-7e288e21440f"
COLLECTION_NAME = "workout_logs"


def get_workout_logs(limit: int = 10) -> list[dict]:
    """Retrieves recent workout logs from the Firestore database.

    Args:
        limit: Maximum number of recent workout logs to retrieve. Defaults to 10.

    Returns:
        List of dictionaries containing workout log details (id, date, exercise, duration_minutes, calories_burned, sets_reps, notes).
    """
    from google.cloud import firestore

    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    docs = db.collection(COLLECTION_NAME).limit(limit).stream()
    logs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        logs.append(data)
    return logs


def log_workout(
    date: str,
    exercise: str,
    duration_minutes: int,
    calories_burned: int,
    sets_reps: str,
    notes: str = "",
) -> dict:
    """Logs a new workout entry in the Firestore database.

    Args:
        date: Date of the workout in YYYY-MM-DD format.
        exercise: Name or type of exercise (e.g., Bench Press, Squat, 5k Run).
        duration_minutes: Duration of workout in minutes.
        calories_burned: Estimated calories burned.
        sets_reps: Details on sets and reps or distance/pace.
        notes: Additional notes or reflections on the workout.

    Returns:
        Dictionary confirming the logged workout and assigned document ID.
    """
    from google.cloud import firestore

    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_data = {
        "date": date,
        "exercise": exercise,
        "duration_minutes": duration_minutes,
        "calories_burned": calories_burned,
        "sets_reps": sets_reps,
        "notes": notes,
    }
    doc_ref.set(doc_data)
    return {"id": doc_ref.id, "status": "logged", "data": doc_data}


STATIC_ASSETS_BUCKET = "qwiklabs-gcp-03-7e288e21440f-static-assets-bucket"


async def generate_fitness_image(
    prompt: str, tool_context: ToolContext = None
) -> str:
    """Generates an image for a fitness, workout, or meal item using gemini-3.1-flash-lite-image in the global region.

    Saves the generated image as an artifact in ADK and uploads it directly to public Cloud Storage,
    returning its public HTTPS URL.

    Args:
        prompt: Description of the fitness item, workout scene, meal, or badge to generate.
        tool_context: Optional ADK ToolContext for saving the artifact.

    Returns:
        The public HTTPS URL of the uploaded image in Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    genai_client = genai.Client(
        project=FIRESTORE_PROJECT_ID,
        location="global",
        vertexai=True,
    )

    response = genai_client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            image_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type or "image/jpeg"
            break

    if not image_bytes:
        raise ValueError("Failed to generate image: no image data returned by model.")

    ext = "png" if "png" in mime_type else "jpg"
    filename = f"fitness_image_{uuid.uuid4().hex[:8]}.{ext}"

    if tool_context and hasattr(tool_context, "save_artifact"):
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename, artifact_part)

    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(STATIC_ASSETS_BUCKET)
    blob_path = f"generated_images/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{STATIC_ASSETS_BUCKET}/{blob_path}"
    return public_url


def consult_fitness_guide(query: str) -> str:
    """Searches the fitness, nutrition, and workout recovery knowledge guide for relevant guidelines and formulas.

    Args:
        query: What to look up (e.g., protein targets, BMR formula, progressive overload, sleep guidelines).

    Returns:
        Relevant passages and guidelines from the fitness guide.
    """
    import os

    guide_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "docs", "fitness_guide.txt"
    )
    if os.path.exists(guide_path):
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        sections = content.split("\n\n")
        matched = [
            s
            for s in sections
            if any(term in s.lower() for term in query_terms)
        ]
        if matched:
            return "\n\n---\n\n".join(matched)
        return content

    return "Fitness guide document not found."

