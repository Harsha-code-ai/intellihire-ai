import random
import requests
import os

# Hugging Face model
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# Read token from environment variable
HF_TOKEN = os.getenv("HF_API_KEY")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# fallback questions (if AI fails)

questions = {
    "python": [
        "What is a Python decorator?",
        "Explain list vs tuple.",
        "What is the GIL?",
        "Explain generators in Python.",
        "What are Python context managers?",
        "Difference between deep copy and shallow copy.",
        "What is a lambda function?",
        "Explain Python multithreading.",
        "What is asyncio in Python?",
        "Explain Python memory management."
    ],
    "backend": [
        "What is REST API?",
        "Explain stateless architecture.",
        "What is JWT authentication?",
        "Difference between SQL and NoSQL.",
        "Explain microservices.",
        "What is API rate limiting?",
        "What is caching in backend systems?",
        "Explain database indexing.",
        "What is load balancing?",
        "Explain message queues."
    ],
    "machine learning": [
        "What is overfitting?",
        "Explain bias vs variance.",
        "What is gradient descent?",
        "What is regularization?",
        "Explain supervised vs unsupervised learning.",
        "What is cross validation?",
        "Explain feature engineering.",
        "What is a neural network?",
        "What is backpropagation?",
        "Explain decision trees."
    ]
}


def generate_question(role: str):

    try:
        prompt = f"Generate one technical interview question for a {role} developer."

        payload = {
            "inputs": prompt
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        result = response.json()

        question = result[0]["generated_text"]

        if question:
            return question

    except:
        pass

    role = role.lower()

    if role in questions:
        return random.choice(questions[role])

    return "Explain your experience with this role."


def evaluate_answer(answer: str):

    try:
        prompt = f"""
        Evaluate the following interview answer.

        Give:
        1. Score from 1 to 10
        2. Short feedback.

        Answer:
        {answer}
        """

        payload = {
            "inputs": prompt
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        result = response.json()

        text = result[0]["generated_text"]

        return {
            "score": 8,
            "feedback": text
        }

    except:

        length = len(answer)

        if length > 200:
            score = 9
            feedback = "Good detailed answer."

        elif length > 100:
            score = 7
            feedback = "Decent answer but can improve."

        else:
            score = 5
            feedback = "Answer is too short."

        return {
            "score": score,
            "feedback": feedback
        }