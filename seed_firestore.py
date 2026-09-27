#!/usr/bin/env python3
"""Seed script for SkillPath AI Firestore database."""

import datetime
from google.cloud import firestore

# Hardcode GCP Project ID explicitly
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-072726f42e52"

def seed_database():
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("learning_paths")

    sample_paths = [
        {
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
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        {
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
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        {
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
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    ]

    print(f"Seeding Firestore project '{FIRESTORE_PROJECT_ID}', collection 'learning_paths'...")
    for item in sample_paths:
        doc_ref = collection_ref.document(item["id"])
        doc_ref.set(item)
        print(f"  ✓ Seeded learning path: {item['id']} - {item['topic']}")

    print("✅ Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
