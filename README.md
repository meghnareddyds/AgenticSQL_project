# AgenticSQL_project
Agentic SQL Query Generator - Agentic AI-Powered Natural Language to SQL Analytics Platform.
AgenticSQL is a full-stack, AI-powered data analytics application that enables users to explore datasets using natural language.

Instead of manually writing SQL queries, users can upload a CSV dataset, ask questions in plain English, and receive AI-generated SQL queries along with actual results from their data.

The application combines Amazon Bedrock, LangGraph, FastAPI, DuckDB, and React to deliver an intelligent and interactive analytics experience.

Features

1. Natural Language to SQL

Ask questions about your dataset in plain English.

Generate SQL queries using Amazon Nova Micro through Amazon Bedrock.

Automatically execute validated, read-only SQL queries.

View generated SQL alongside query results.

Example:

Question:

Give me the top 5 sold products.

Generated SQL:

SELECT
    product,
    SUM(quantity) AS total_quantity
FROM sales_data
GROUP BY product
ORDER BY total_quantity DESC
LIMIT 5;

Example Results:

Product

Total Quantity

Desk

352

Monitor

323

Headphones

318

Webcam

288

Office Chair

286

Results shown are from the included sample sales dataset.

2. AI Agent Workflow with LangGraph

AgenticSQL uses LangGraph to coordinate the natural-language-to-SQL workflow.

The agent processes a user's question, generates SQL, validates it, executes the query, and returns structured results.

Workflow:

User Question
      |
      v
Read Dataset Schema
      |
      v
Amazon Bedrock (Nova Micro)
      |
      v
Generate SQL Query
      |
      v
SQLGlot Validation
      |
      v
DuckDB Query Execution
      |
      v
Return SQL + Query Results
      |
      v
React Frontend

3. CSV Dataset Upload

Upload CSV files through the web interface.

Automatically detect column names and data types.

Store uploaded data in a local DuckDB database.

View dataset metadata, including column types and total row count.

4. SQL Analytics Workspace

Write and execute SQL queries manually.

View SQL query results in a structured table.

Explore uploaded datasets without relying entirely on AI-generated queries.

5. AI Chat

Interact with Amazon Nova Micro through Amazon Bedrock.

Ask general SQL-related questions.

Switch to dataset analysis when you want to query uploaded data.

6. SQL Safety Controls

Validate generated SQL using SQLGlot.

Restrict query execution to supported read-only operations.

Limit returned results.

Execute queries through a read-only database connection.

Note: The current implementation is intended for local development and demonstration. Additional authentication, resource limits, and security hardening would be required before public deployment.

🛠️ Tech Stack

Layer

Technology

Frontend

React, TypeScript, Vite

Backend

Python, FastAPI

AI Model

Amazon Nova Micro

LLM Platform

Amazon Bedrock

Agent Orchestration

LangGraph

Database

DuckDB

SQL Validation

SQLGlot

AWS Integration

Boto3

Version Control

Git and GitHub

🏗️ Project Architecture

                  ┌───────────────────────┐
                  │     React Frontend    │
                  │    TypeScript + Vite  │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │     FastAPI Backend   │
                  │                       │
                  │  /api/chat            │
                  │  /api/agent/query     │
                  │  /api/upload          │
                  │  /api/schema          │
                  │  /api/query           │
                  └───────────┬───────────┘
                              │
                  ┌───────────▼───────────┐
                  │    LangGraph Agent    │
                  │                       │
                  │  SQL Generation       │
                  │  SQL Validation       │
                  │  Query Execution      │
                  └───────┬───────┬───────┘
                          │       │
             ┌────────────▼┐    ┌─▼─────────────┐
             │ Amazon      │    │ DuckDB        │
             │ Bedrock     │    │ Local SQL     │
             │ Nova Micro  │    │ Database      │
             └─────────────┘    └───────────────┘

📂 Project Structure

AgenticSQL_project/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   ├── test_sql_agent.py
│   └── test_sql_generation.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.ts
│
├── sample_data/
│   ├── generate_sales.py
│   └── sales.csv
│
└── README.md

⚙️ Getting Started

Prerequisites

Make sure you have:

Python 3.10 or newer

Node.js and npm

Git

An AWS account with access to Amazon Bedrock

AWS CLI configured with credentials authorized to invoke Amazon Nova Micro

Step 1: Clone the Repository

git clone https://github.com/meghnareddyds/AgenticSQL_project.git
cd AgenticSQL_project

Step 2: Set Up the Backend

On Windows PowerShell:

cd backend

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Step 3: Configure AWS Credentials

Install the AWS CLI and configure a named profile:

aws configure --profile agenticsql

Set the AWS profile and region for the current PowerShell session:

$env:AWS_PROFILE = "agenticsql"
$env:AWS_DEFAULT_REGION = "us-east-2"

Security: Never commit AWS access keys, credentials, or .env files to GitHub.

Step 4: Start the Backend

From the backend directory:

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

The backend runs at:

http://localhost:8000

FastAPI API documentation:

http://localhost:8000/docs

Step 5: Start the Frontend

Open a second terminal:

cd frontend

npm install

npm run dev

Open the local URL displayed by Vite, typically:

http://localhost:5173

Step 6: Upload a Dataset

Open the application in your browser.

Navigate to Dataset Management.

Upload sample_data/sales.csv.

Verify that the table schema and row count appear.

Select Analyze Data and ask a question about the dataset.

Example Questions

Try asking AgenticSQL:

What are the top 5 products by quantity sold?

Which region generated the highest revenue?

What is the total revenue?

How many orders are in the dataset?

What is the average order value?

Which product category generates the most revenue?

AgenticSQL generates SQL based on the available dataset schema and returns the query results.

API Endpoints

Method

Endpoint

Description

GET

/health

Check backend health

GET

/api/schema

Retrieve dataset schema

POST

/api/upload

Upload a CSV dataset

POST

/api/query

Execute a validated SQL query

POST

/api/chat

Ask the Bedrock-powered AI assistant

POST

/api/agent/query

Run the natural-language-to-SQL agent

Interactive API documentation is available through FastAPI's Swagger UI.

 Testing

The project includes scripts for testing SQL generation and the agent workflow.

From the project root, activate the backend virtual environment and run:

.\backend\.venv\Scripts\python.exe backend\test_sql_generation.py

.\backend\.venv\Scripts\python.exe backend\test_sql_agent.py

To verify the frontend production build:

cd frontend
npm run build

🔒 Security and Cost Considerations

The application includes SQL validation and read-only execution controls, but these should not be treated as a complete security boundary for untrusted users.

Amazon Bedrock model inference is usage-based and may incur AWS charges. Monitor usage through AWS Billing and Cost Management, and avoid exposing your AWS credentials.

🎯 Project Goal

AgenticSQL demonstrates how generative AI and agent-based workflows can simplify data exploration by translating natural-language questions into executable SQL queries.

The project brings together full-stack development, cloud-based language models, database querying, and AI orchestration in a practical analytics application.

👩‍💻 Author

Meghna Reddy

GitHub: meghnareddyds
