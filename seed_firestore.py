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
            "description": "Comprehensive learning path covering foundational Computer Science theory (MIT & Harvard) followed by practical Data Science implementation (Coursera & edX).",
            "steps": [
                {
                    "step_number": 1,
                    "title": "THEORY FIRST: Computational Thinking & Math Foundations",
                    "description": "Master algorithmic complexity (Big-O), memory allocation, and discrete mathematics for data science.",
                    "resources": [
                        {"title": "MIT 6.0001: Intro to Computer Science & Python (MIT OpenCourseWare)", "type": "university_course", "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/"},
                        {"title": "Harvard CS50P: Introduction to Programming with Python (Harvard University / edX)", "type": "university_course", "url": "https://cs50.harvard.edu/python/"}
                    ]
                },
                {
                    "step_number": 2,
                    "title": "PRACTICAL SKILL COURSES: Data Manipulation & Analysis",
                    "description": "Apply core theory through vectorized computing with NumPy, Pandas dataframes, and data visualization.",
                    "resources": [
                        {"title": "Applied Data Science with Python Specialization (University of Michigan / Coursera)", "type": "provider_course", "url": "https://www.coursera.org/specializations/data-science-python"},
                        {"title": "Google Data Analytics Professional Certificate (Google / Coursera)", "type": "provider_course", "url": "https://www.coursera.org/professional-certificates/google-data-analytics"}
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
            "description": "Full-stack path structuring Web Architecture Theory first (Harvard & Oxford) before practical frontend/backend skill courses (Meta & Udacity).",
            "steps": [
                {
                    "step_number": 1,
                    "title": "THEORY FIRST: Web Architecture & Internet Protocol Foundations",
                    "description": "Understand HTTP/HTTPS protocols, TCP/IP networking, DOM tree algorithms, and database relational theory.",
                    "resources": [
                        {"title": "Harvard CS50W: Web Programming with Python and JavaScript (Harvard University)", "type": "university_course", "url": "https://cs50.harvard.edu/web/"},
                        {"title": "Stanford CS142: Web Applications (Stanford University)", "type": "university_course", "url": "https://web.stanford.edu/class/cs142/"}
                    ]
                },
                {
                    "step_number": 2,
                    "title": "PRACTICAL SKILL COURSES: Modern Full-Stack Implementation",
                    "description": "Build end-to-end full-stack web applications with FastAPI, React, RESTful APIs, and Cloud deployment.",
                    "resources": [
                        {"title": "Meta Front-End & Back-End Developer Certificates (Meta / Coursera)", "type": "provider_course", "url": "https://www.coursera.org/meta"},
                        {"title": "Full Stack Web Developer Nanodegree (Udacity)", "type": "provider_course", "url": "https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044"}
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
            "description": "Rigorous AI roadmap covering Linear Algebra & Probability Theory first (Stanford & MIT), followed by applied ML skill courses (DeepLearning.AI & Google Cloud).",
            "steps": [
                {
                    "step_number": 1,
                    "title": "THEORY FIRST: Mathematical Principles & Machine Learning Theory",
                    "description": "Study gradient descent mathematical proofs, matrix calculus, probability distributions, and loss minimization theory.",
                    "resources": [
                        {"title": "Stanford CS229: Machine Learning (Stanford University / Andrew Ng)", "type": "university_course", "url": "https://cs229.stanford.edu/"},
                        {"title": "MIT 18.06: Linear Algebra & Optimization (MIT OpenCourseWare)", "type": "university_course", "url": "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/"}
                    ]
                },
                {
                    "step_number": 2,
                    "title": "PRACTICAL SKILL COURSES: Applied Machine Learning & MLOps",
                    "description": "Implement supervised and unsupervised algorithms with Scikit-Learn, PyTorch, and Vertex AI MLOps pipelines.",
                    "resources": [
                        {"title": "Machine Learning Specialization (DeepLearning.AI & Stanford / Coursera)", "type": "provider_course", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
                        {"title": "Google Cloud Machine Learning Engineer Learning Path (Google Cloud Skills Boost)", "type": "provider_course", "url": "https://www.cloudskillsboost.google/paths/17"}
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
