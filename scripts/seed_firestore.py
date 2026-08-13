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

"""Seed script to populate Firestore database with initial workout logs."""

from google.cloud import firestore

# CRITICAL: Hardcoded GCP project ID string as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-03-7e288e21440f"
COLLECTION_NAME = "workout_logs"

SEED_DATA = [
    {
        "id": "log_001",
        "date": "2026-08-10",
        "exercise": "Bench Press & Upper Body",
        "duration_minutes": 50,
        "calories_burned": 380,
        "sets_reps": "4 x 10 @ 185 lbs bench, 3 x 12 incline dumbbell press",
        "notes": "Great chest workout, felt energetic after pre-workout meal.",
    },
    {
        "id": "log_002",
        "date": "2026-08-11",
        "exercise": "Leg Day (Squats & Deadlifts)",
        "duration_minutes": 60,
        "calories_burned": 450,
        "sets_reps": "5 x 5 @ 245 lbs squat, 3 x 8 @ 275 lbs deadlift",
        "notes": "Hit a personal best on squats. Make sure to stretch hamstrings.",
    },
    {
        "id": "log_003",
        "date": "2026-08-12",
        "exercise": "Cardio & Core (5k Run)",
        "duration_minutes": 30,
        "calories_burned": 320,
        "sets_reps": "5km run @ 5:30/km pace, 3 x 20 plank-to-pushups",
        "notes": "Active recovery day. Kept heart rate around 145 bpm.",
    },
]


def seed_firestore():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding Firestore collection '{COLLECTION_NAME}' in project '{PROJECT_ID}'...")
    for item in SEED_DATA:
        doc_id = item["id"]
        doc_data = {k: v for k, v in item.items() if k != "id"}
        collection_ref.document(doc_id).set(doc_data)
        print(f" - Seeded document '{doc_id}': {doc_data['exercise']}")

    print("Seeding complete!")


if __name__ == "__main__":
    seed_firestore()
