# IntelliHire AI Interview Platform

IntelliHire is an AI-powered interview preparation platform that helps users practice technical interviews, analyze resumes, and track interview performance.

The platform generates role-based interview questions, evaluates answers, analyzes resumes for skill gaps, and stores interview history.


## Features

AI Interview Question Generator  
Generates role-specific technical interview questions.

AI Answer Evaluation  
Evaluates answers and provides feedback with a score.

Resume Analyzer  
Detects skills in the resume and identifies missing skills.

Skill Match Percentage  
Shows how well a resume matches a specific role.

Interview History  
Stores previous interview attempts and scores.

Modern Web Interface  
Interactive frontend built with React.



## Tech Stack

Frontend  
React (Vite)

Backend  
FastAPI (Python)

Database  
SQLite

AI Integration  
Hugging Face Transformer Models

Deployment  
Vercel (Frontend)  
Render (Backend)



## Project Structure


intellihire-pro
backend
app
api
services
models

frontend
src
components


---

## Installation

### Clone Repository


git clone https://github.com/Harsha-code-ai/intellihire-ai





### Backend Setup


cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload


Backend will run at


http://127.0.0.1:8000




### Frontend Setup


cd frontend
npm install
npm run dev


Frontend will run at


http://localhost:5173



## Future Improvements

AI-based answer evaluation using large language models  
Better resume parsing using NLP  
User authentication system  
Admin dashboard for analytics



## Author

Harsha Vardhan Reddy B 
AIML Student – Chandigarh University