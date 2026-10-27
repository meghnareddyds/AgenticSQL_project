
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
import os
from app.services.bedrock_service import ask_bedrock



from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.database import (
    initialize_database,
    replace_dataset,
    get_schema,
    execute_readonly_query,
)
from app.services.sql_guard import validate_sql


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="AgenticSQL API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class SQLRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=5000)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AgenticSQL Backend",
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        answer = ask_bedrock(request.question)

        return {
            "question": request.question,
            "answer": answer,
            "status": "success",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        print(f"Bedrock error: {exc}")

        raise HTTPException(
            status_code=502,
            detail="Unable to get a response from Amazon Bedrock.",
        ) from exc


@app.get("/api/schema")
def schema():
    return get_schema()


@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are supported",
        )

    max_size = 5 * 1024 * 1024
    total_size = 0
    temp_path = None

    try:
        with NamedTemporaryFile(
            mode="wb", suffix=".csv", delete=False
        ) as temp:
            temp_path = Path(temp.name)

            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail="CSV exceeds 5 MB limit",
                    )

                temp.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty",
            )

        try:
            replace_dataset(temp_path)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"CSV could not be imported: {exc}",
            ) from exc

        return {
            "message": "CSV uploaded successfully",
            "schema": get_schema(),
        }

    finally:
        await file.close()
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass


@app.post("/api/query")
def run_query(request: SQLRequest):
    try:
        schema_info = get_schema()
        columns = [
            col["name"] for col in schema_info["columns"]
        ]

        validated_sql = validate_sql(
            request.sql, columns
        )

        result = execute_readonly_query(validated_sql)

        return {
            "sql": validated_sql,
            **result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Query failed: {exc}",
        ) from exc
