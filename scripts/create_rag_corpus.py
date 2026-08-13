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

"""Script to create a serverless Vertex AI RAG Corpus and index fitness_guide.txt."""

import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-03-7e288e21440f"
LOCATION = "us-central1"
GCS_PATH = "gs://agent-staging-bucket-qwiklabs-gcp-03-7e288e21440f/rag/fitness_guide.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, formulas, and fitness/nutrition guidelines described in this text. "
    "Ignore and omit all metadata, boilerplate, and formatting symbols. "
    "Output clean, self-contained prose."
)


def create_and_populate_corpus():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print(f"Setting RAG Engine config to serverless mode for project '{PROJECT_ID}'...")
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )

    print("Creating serverless RAG corpus...")
    corpus = rag.create_corpus(
        display_name="fitness-guide-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print("CORPUS_NAME:", corpus.name)

    print(f"Importing and indexing document from '{GCS_PATH}'...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print("Successfully imported files count:", resp.imported_rag_files_count)
    return corpus.name


if __name__ == "__main__":
    create_and_populate_corpus()
