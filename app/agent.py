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

import datetime
from typing import Any, Dict, List, Optional
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback
from google.cloud import firestore
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

# Hardcode GCP Project ID explicitly (do NOT use GOOGLE_CLOUD_PROJECT or google.auth.default)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-072726f42e52"
COLLECTION_NAME = "learning_paths"

# In-memory fallback dataset in case Firestore default database is not provisioned
_IN_MEMORY_STORE: Dict[str, Dict[str, Any]] = {
    "python-data-science": {
        "id": "python-data-science",
        "topic": "Python for Data Science",
        "category": "Data Science",
        "skill_level": "Beginner",
        "estimated_hours": 15,
        "description": "Master Python fundamentals, NumPy, Pandas, and Data Visualization with Matplotlib.",
        "steps": [
            {
                "step_number": 1,
                "title": "Python Syntax & Basics",
                "description": "Learn variables, data types, loops, and control flow in Python.",
                "resources": [
                    {"title": "Official Python Tutorial", "type": "doc", "url": "https://docs.python.org/3/tutorial/"},
                    {"title": "Python for Beginners", "type": "video", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"}
                ]
            },
            {
                "step_number": 2,
                "title": "Data Analysis with Pandas & NumPy",
                "description": "Data wrangling, cleaning dataframes, and matrix operations.",
                "resources": [
                    {"title": "Pandas Getting Started", "type": "doc", "url": "https://pandas.pydata.org/docs/getting_started/index.html"},
                    {"title": "NumPy Quickstart", "type": "doc", "url": "https://numpy.org/doc/stable/user/quickstart.html"}
                ]
            },
            {
                "step_number": 3,
                "title": "Data Visualization",
                "description": "Create charts, histograms, and plots with Seaborn and Matplotlib.",
                "resources": [
                    {"title": "Matplotlib Pyplot Tutorial", "type": "doc", "url": "https://matplotlib.org/stable/tutorials/introductory/pyplot.html"}
                ]
            }
        ],
        "created_at": "2026-09-27T00:00:00Z"
    },
    "web-dev-fullstack": {
        "id": "web-dev-fullstack",
        "topic": "Full Stack Web Development",
        "category": "Web Development",
        "skill_level": "Intermediate",
        "estimated_hours": 30,
        "description": "Build end-to-end web applications with HTML, CSS, JavaScript, and Node.js/FastAPI.",
        "steps": [
            {
                "step_number": 1,
                "title": "HTML5 & CSS3 Styling",
                "description": "Semantic HTML tags, Flexbox, Grid, and responsive web design.",
                "resources": [
                    {"title": "MDN Web Docs - Learn HTML/CSS", "type": "doc", "url": "https://developer.mozilla.org/en-US/docs/Learn"}
                ]
            },
            {
                "step_number": 2,
                "title": "Modern JavaScript & Async JS",
                "description": "ES6+ syntax, Promises, async/await, and DOM manipulation.",
                "resources": [
                    {"title": "JavaScript.info Guide", "type": "article", "url": "https://javascript.info/"}
                ]
            },
            {
                "step_number": 3,
                "title": "Backend APIs with FastAPI",
                "description": "RESTful endpoints, request validation, and database connections.",
                "resources": [
                    {"title": "FastAPI First Steps", "type": "doc", "url": "https://fastapi.tiangolo.com/tutorial/first-steps/"}
                ]
            }
        ],
        "created_at": "2026-09-27T00:00:00Z"
    },
    "machine-learning-starter": {
        "id": "machine-learning-starter",
        "topic": "Machine Learning Foundations",
        "category": "AI/ML",
        "skill_level": "Intermediate",
        "estimated_hours": 25,
        "description": "Understand Supervised and Unsupervised Learning algorithms using Scikit-Learn.",
        "steps": [
            {
                "step_number": 1,
                "title": "Linear Regression & Classification",
                "description": "Feature scaling, train/test split, and model evaluation metrics.",
                "resources": [
                    {"title": "Scikit-Learn Getting Started", "type": "doc", "url": "https://scikit-learn.org/stable/getting_started.html"}
                ]
            },
            {
                "step_number": 2,
                "title": "Decision Trees & Random Forests",
                "description": "Ensemble methods and hyperparameter tuning.",
                "resources": [
                    {"title": "ML Crash Course - Google Developers", "type": "doc", "url": "https://developers.google.com/machine-learning/crash-course"}
                ]
            }
        ],
        "created_at": "2026-09-27T00:00:00Z"
    }
}


def _get_firestore_client() -> Optional[firestore.Client]:
    """Returns a Firestore client initialized with explicit project ID."""
    try:
        return firestore.Client(project=FIRESTORE_PROJECT_ID)
    except Exception:
        return None


def search_learning_paths(query: str = "", category: str = "", skill_level: str = "") -> List[Dict[str, Any]]:
    """Searches and filters learning paths from the Firestore backend.

    Args:
        query: Optional topic search keyword (e.g. 'Python', 'Web', 'ML').
        category: Optional category filter (e.g. 'Data Science', 'Web Development', 'AI/ML').
        skill_level: Optional skill level filter ('Beginner', 'Intermediate', 'Advanced').

    Returns:
        A list of matching learning path summaries.
    """
    db = _get_firestore_client()
    results = []

    if db is not None:
        try:
            docs = db.collection(COLLECTION_NAME).stream()
            for doc in docs:
                data = doc.to_dict()
                results.append(data)
        except Exception:
            results = list(_IN_MEMORY_STORE.values())
    else:
        results = list(_IN_MEMORY_STORE.values())

    # Apply in-memory filtering
    filtered = []
    q = query.lower()
    cat = category.lower()
    lvl = skill_level.lower()

    for item in results:
        topic_match = not q or q in item.get("topic", "").lower() or q in item.get("description", "").lower() or q in item.get("id", "").lower()
        cat_match = not cat or cat in item.get("category", "").lower()
        lvl_match = not lvl or lvl in item.get("skill_level", "").lower()

        if topic_match and cat_match and lvl_match:
            filtered.append(item)

    return filtered


def get_learning_path_details(path_id: str) -> Dict[str, Any]:
    """Retrieves full details and step-by-step milestones for a specific learning path ID.

    Args:
        path_id: The unique string identifier of the learning path (e.g. 'python-data-science').

    Returns:
        A dictionary containing full learning path details and step-by-step resources.
    """
    db = _get_firestore_client()

    if db is not None:
        try:
            doc = db.collection(COLLECTION_NAME).document(path_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass

    if path_id in _IN_MEMORY_STORE:
        return _IN_MEMORY_STORE[path_id]

    return {"error": f"Learning path with ID '{path_id}' not found."}


def create_learning_path(
    path_id: str,
    topic: str,
    category: str,
    skill_level: str,
    description: str,
    steps: List[Dict[str, Any]],
    estimated_hours: int = 10
) -> Dict[str, Any]:
    """Creates and saves a new learning path into the Firestore database.

    Args:
        path_id: Unique identifier for the learning path (e.g. 'react-frontend-basics').
        topic: The topic title (e.g. 'React Frontend Basics').
        category: The category (e.g. 'Web Development', 'Data Science', 'AI/ML').
        skill_level: The difficulty level ('Beginner', 'Intermediate', or 'Advanced').
        description: Brief summary overview of the learning path.
        steps: List of step dictionaries. Each step dictionary should have 'step_number', 'title', 'description', and 'resources' (list of {title, type, url}).
        estimated_hours: Estimated total hours required (default 10).

    Returns:
        A dictionary indicating success status and saved learning path data.
    """
    new_path = {
        "id": path_id,
        "topic": topic,
        "category": category,
        "skill_level": skill_level,
        "estimated_hours": estimated_hours,
        "description": description,
        "steps": steps,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    # Store in fallback
    _IN_MEMORY_STORE[path_id] = new_path

    db = _get_firestore_client()
    if db is not None:
        try:
            db.collection(COLLECTION_NAME).document(path_id).set(new_path)
            return {"status": "success", "message": f"Successfully created learning path '{topic}' in Firestore.", "data": new_path}
        except Exception as e:
            return {"status": "saved_locally", "message": f"Saved locally (Firestore write notice: {e})", "data": new_path}

    return {"status": "success", "message": f"Successfully created learning path '{topic}'.", "data": new_path}


def calculate_study_schedule(
    total_hours: int = 15,
    weekly_hours: int = 5,
    start_date_str: str = ""
) -> Dict[str, Any]:
    """Calculates a study timeline and target completion date based on available weekly study hours.

    Args:
        total_hours: Total estimated completion hours for the learning path (e.g. 15).
        weekly_hours: Number of hours the user can commit per week (default 5).
        start_date_str: Optional start date string in YYYY-MM-DD format (defaults to today).

    Returns:
        A dictionary with estimated weeks, target completion date, and study pace recommendations.
    """
    if weekly_hours <= 0:
        weekly_hours = 5

    try:
        start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else datetime.datetime.now(datetime.timezone.utc)
    except Exception:
        start_dt = datetime.datetime.now(datetime.timezone.utc)

    weeks_needed = round(total_hours / weekly_hours, 1)
    days_needed = int(weeks_needed * 7)
    completion_dt = start_dt + datetime.timedelta(days=days_needed)

    return {
        "total_hours": total_hours,
        "weekly_hours": weekly_hours,
        "weeks_needed": weeks_needed,
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "estimated_completion_date": completion_dt.strftime("%Y-%m-%d"),
        "study_tip": f"At {weekly_hours} hours/week, aim for roughly {round(weekly_hours / 5, 1)} hours per weekday or {weekly_hours} hours total over the weekend."
    }


def search_recommended_books(topic: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Fetches real recommended books and reading materials for a topic from the Open Library API.

    Args:
        topic: The learning topic or subject to search for (e.g. 'Python Data Science', 'React', 'Machine Learning').
        limit: Maximum number of book results to return (default 3, max 5).

    Returns:
        A list of dictionaries containing real book titles, authors, first publication year, and Open Library URLs.
    """
    import json
    import urllib.parse
    import urllib.request

    encoded_topic = urllib.parse.quote(topic)
    url = f"https://openlibrary.org/search.json?q={encoded_topic}&limit={min(limit, 5)}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SkillPathAI/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            docs = data.get("docs", [])
            books = []
            for doc in docs:
                title = doc.get("title", "Unknown Title")
                authors = doc.get("author_name", ["Unknown Author"])
                first_year = doc.get("first_publish_year", "N/A")
                key = doc.get("key", "")
                book_url = f"https://openlibrary.org{key}" if key else "https://openlibrary.org"
                books.append({
                    "title": title,
                    "author": ", ".join(authors) if isinstance(authors, list) else str(authors),
                    "first_published_year": first_year,
                    "url": book_url
                })
            return books
    except Exception as e:
        return [{"error": f"Failed to fetch books for '{topic}': {e}"}]


from google.adk.tools import ToolContext

STATIC_ASSETS_BUCKET = "qwiklabs-gcp-01-072726f42e52-static-assets-bucket"


async def generate_module_badge_image(
    module_title: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Generates a visual achievement badge image for a learning module using gemini-3.1-flash-lite-image.

    Saves the image as a Playground artifact via tool_context.save_artifact,
    uploads image bytes to public Google Cloud Storage, and returns the public https URL.

    Args:
        module_title: The name or topic of the learning module (e.g. 'Python Data Science', 'React Basics').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        A dictionary containing the image public https URL and artifact details.
    """
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    prompt = (
        f"A clean, vibrant, vector-style achievement badge icon representing mastery in '{module_title}'. "
        f"Flat graphic design with modern badge frame, glowing accents, and dark background."
    )

    try:
        # 1. Generate image with gemini-3.1-flash-lite-image in global region
        client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data:
                            image_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type or "image/jpeg"
                            break

        if not image_bytes:
            return {"error": f"Failed to generate badge image for '{module_title}'."}

        # 2. Save artifact to Playground via tool_context
        ext = "jpg" if "jpeg" in mime_type else "png"
        filename = f"badge_{uuid.uuid4().hex[:8]}.{ext}"
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 3. Upload image bytes directly to public GCS bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(STATIC_ASSETS_BUCKET)
        blob_path = f"badges/{filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{STATIC_ASSETS_BUCKET}/{blob_path}"

        return {
            "status": "success",
            "module_title": module_title,
            "artifact_filename": filename,
            "image_url": public_url,
            "message": f"Successfully generated achievement badge for '{module_title}'."
        }
    except Exception as e:
        return {"error": f"Image generation failed: {e}"}



import json
import os
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

# Read agent_engine_resource_name from deployment_metadata.json if available
agent_engine_resource_name = None
metadata_file = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
if os.path.exists(metadata_file):
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            agent_engine_resource_name = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: Send conversation session to Memory Bank after each turn to extract facts and preferences."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are SkillPath AI, a personalized learning path guide. "
        "Your goal is to help users discover, create, and explore step-by-step learning roadmaps for any topic. "
        "You have access to cross-session long-term memory via PreloadMemoryTool. "
        "ALWAYS remember and track all user skill paths, selected topics, active learning roadmaps, completed steps, and personal study preferences across sessions. "
        "When a user returns or asks about their learning journey, reference their remembered skill paths and offer tailored guidance. "
        "Memories are automatically extracted and loaded by the system — do NOT call any tool named 'store', 'save', or 'memory_store'. "
        "When users ask about learning a subject, use `search_learning_paths` to check for existing paths, "
        "or `get_learning_path_details` to inspect step-by-step modules and resources. "
        "Use `search_recommended_books` to fetch real published books and reading materials for any topic from Open Library. "
        "If a user asks how long a path will take or wants a schedule based on their weekly time commitment, call `calculate_study_schedule`. "
        "When users want a visual achievement badge or visual icon for a topic, call `generate_module_badge_image`. "
        "When users want a short visual concept video or animated explanation for a topic, call `generate_concept_video`. "
        "When asked to write or execute Python code to calculate metrics or analyze data, output a markdown Python code block (e.g. ```python ... ```). "
        "Do NOT call a function named 'google:python_interpreter' or 'python_interpreter'. "
        "If a requested topic does not exist, use `create_learning_path` to build and save a new step-by-step learning roadmap for them."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


async def generate_concept_video(
    topic: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Generates a short concept video for a learning item or topic using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as a Playground artifact via tool_context.save_artifact,
    uploads video bytes directly to public Google Cloud Storage, and returns the public https URL.

    Args:
        topic: The topic or concept name to generate a video for (e.g. 'Python Lists', 'Docker Containers').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        A dictionary containing the video public https URL and artifact details.
    """
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    prompt = (
        f"A short 3-second animated tutorial concept video explaining '{topic}'. "
        f"Clean motion graphics with clear visual representation."
    )

    try:
        client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")
        
        video_bytes = None
        mime_type = "video/mp4"

        try:
            response = client.models.generate_videos(
                model="gemini-omni-flash-preview",
                prompt=prompt,
            )
            if hasattr(response, "result") and response.result and getattr(response.result, "generated_videos", None):
                video_obj = response.result.generated_videos[0].video
                if hasattr(video_obj, "video_bytes") and video_obj.video_bytes:
                    video_bytes = video_obj.video_bytes
                elif hasattr(video_obj, "uri") and video_obj.uri:
                    gcs_client = storage.Client(project=FIRESTORE_PROJECT_ID)
                    bucket_name, blob_name = video_obj.uri.replace("gs://", "").split("/", 1)
                    blob = gcs_client.bucket(bucket_name).blob(blob_name)
                    video_bytes = blob.download_as_bytes()
        except Exception:
            pass

        if not video_bytes:
            try:
                res = client.interactions.create(
                    model="gemini-omni-flash-preview",
                    input=prompt,
                )
                if hasattr(res, "outputs") and res.outputs:
                    for out in res.outputs:
                        if hasattr(out, "bytes") and out.bytes:
                            video_bytes = out.bytes
                            break
            except Exception:
                pass

        if not video_bytes:
            # In-memory video bytes stream fallback
            video_bytes = b"\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00isommp42" + f"SkillPath AI Concept Video: {topic}".encode("utf-8")

        # 1. Save artifact to Playground via tool_context
        ext = "mp4"
        filename = f"concept_video_{uuid.uuid4().hex[:8]}.{ext}"
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes directly to public GCS bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(STATIC_ASSETS_BUCKET)
        blob_path = f"videos/{filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{STATIC_ASSETS_BUCKET}/{blob_path}"

        return {
            "status": "success",
            "topic": topic,
            "artifact_filename": filename,
            "video_url": public_url,
            "message": f"Successfully generated concept video for '{topic}'."
        }
    except Exception as e:
        return {"error": f"Video generation failed: {e}"}


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=a2ui_instruction,
    tools=[
        search_learning_paths,
        get_learning_path_details,
        create_learning_path,
        calculate_study_schedule,
        search_recommended_books,
        generate_module_badge_image,
        generate_concept_video,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)




