# Multiplayer Quiz Backend

A FastAPI-based backend for a multiplayer quiz application. It supports user authentication, quiz and question management, and real-time multiplayer game rooms using WebSockets. *Project built to learn WebSockets*

## Features

- JWT-based signup and login flow
- User profile retrieval via authenticated requests
- Quiz creation, listing, update, and deletion
- Question creation, update, and deletion for each quiz
- Host-managed multiplayer room creation with unique room codes
- Real-time quiz lifecycle over WebSockets
- Answer validation and room state updates for live gameplay

## Tech Stack

- Python 3.14+
- FastAPI
- SQLAlchemy
- SQLite (configurable via DATABASE_URL)
- WebSockets for multiplayer room communication

## Project Structure

```text
.
├── database/
│   ├── db.py
│   ├── models.py
│   └── questions.db
├── models/
│   ├── question.py
│   ├── quiz.py
│   ├── room.py
│   └── user.py
├── routers/
│   ├── question.py
│   ├── quiz.py
│   ├── room.py
│   └── user.py
├── storage/
│   ├── question.py
│   ├── quiz.py
│   ├── room.py
│   └── user.py
├── utils/
│   ├── connections.py
│   ├── security.py
│   └── ...
├── .env
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

1. Clone the repository.
2. Create a `.env` file in the project root.
3. Set a database connection string:

```env
DATABASE_URL=sqlite:///database/questions.db
```

You can swap the SQLite URL for another SQLAlchemy-supported database if needed.

## Installation

Using `uv` (recommended):

```bash
uv sync
```

## Running the Server

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Overview

### Authentication

- `POST /users/signup` — create a user account
- `POST /users/login` — login and receive a JWT token
- `GET /users/me` — get authenticated user details

### Quizzes

- `GET /quizzes` — list quizzes
- `GET /quizzes/{quiz_id}` — get a quiz by ID
- `POST /quizzes` — create a quiz
- `PATCH /quizzes/{quiz_id}` — update a quiz
- `DELETE /quizzes/{quiz_id}` — delete a quiz

### Questions

- `GET /quizzes/{quiz_id}/questions` — list questions for a quiz
- `GET /quizzes/{quiz_id}/questions/{question_id}` — get a question by ID
- `POST /quizzes/{quiz_id}/questions` — create a question
- `PATCH /quizzes/{quiz_id}/questions/{question_id}` — update a question
- `DELETE /quizzes/{quiz_id}/questions/{question_id}` — delete a question

### Rooms

- `POST /rooms` — create a room for a quiz
- `GET /rooms/{room_id}` — get room details
- `WS /rooms/{room_id}` — real-time multiplayer room WebSocket endpoint

## Notes

- Only the quiz author can modify or delete their own quiz.
- Only quiz owners can create rooms from their quizzes.
- Room gameplay is coordinated through WebSockets and host-controlled actions.
