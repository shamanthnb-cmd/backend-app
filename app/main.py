
import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "testuser"),
        password=os.getenv("DB_PASSWORD", "testpass"),
        dbname=os.getenv("DB_NAME", "testdb"),
    )


@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.get("/db-check")
def database_check():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        return {
            "status": "success",
            "database": "PostgreSQL connected",
            "result": result[0],
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {error}",
        )


class User(BaseModel):
    name: str
    email: str


@app.post("/users")
def create_user(user: User):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        email VARCHAR(150)
                    )
                """)

                cursor.execute(
                    """
                    INSERT INTO users (name, email)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (user.name, user.email),
                )

                user_id = cursor.fetchone()[0]

        return {
            "message": "User created successfully",
            "user_id": user_id,
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/users")
def get_users():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, email FROM users ORDER BY id" )
                users = cursor.fetchall()

        return [{"id": row[0], "name": row[1], "email": row[2]} for row in users] 

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
