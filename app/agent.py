# ruff: noqa
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

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.tools import (
    add,
    calculate_factorial,
    consult_fitness_guide,
    divide,
    generate_fitness_image,
    get_workout_logs,
    log_workout,
    multiply,
    power,
    subtract,
)

MODEL = "gemini-2.5-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a friendly, encouraging, and highly competent Fitness & Workout Coach. "
        "You remember the user's stated health goals, dietary restrictions, workout history, and personal bests "
        "from previous conversations to personalize your guidance. "
        "Use your workout log tools (get_workout_logs, log_workout) to track workouts, "
        "consult_fitness_guide to look up macronutrient & recovery guidelines, "
        "generate_fitness_image to generate visual workout scenes or meal items, "
        "and your calculation tools step-by-step."
    ),
    tools=[
        PreloadMemoryTool(),
        get_workout_logs,
        log_workout,
        consult_fitness_guide,
        generate_fitness_image,
        add,
        subtract,
        multiply,
        divide,
        power,
        calculate_factorial,
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
