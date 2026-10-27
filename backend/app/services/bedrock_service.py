import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound


AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_PROFILE = os.getenv("AWS_PROFILE", "agenticsql")
MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "us.amazon.nova-micro-v1:0",
)


def ask_bedrock(question: str) -> str:
    """
    Send a question to Amazon Nova Micro
    and return the generated text.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    try:
        session = boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )

        client = session.client("bedrock-runtime")

        response = client.converse(
            modelId=MODEL_ID,
            system=[
                {
                    "text": (
                        "You are AgenticSQL, a helpful SQL and "
                        "data analytics assistant. "
                        "Explain concepts clearly and concisely. "
                        "Do not claim to have executed SQL queries "
                        "or inspected datasets unless you have "
                        "actually done so."
                    )
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": question}],
                }
            ],
            inferenceConfig={
                "maxTokens": 150,
                "temperature": 0,
            },
        )

        content = response["output"]["message"]["content"]

        answer = "\n".join(
            block["text"]
            for block in content
            if "text" in block
        )

        return answer or "The model returned an empty response."

    except (ClientError, BotoCoreError, ProfileNotFound) as error:
        raise RuntimeError(
            f"Amazon Bedrock request failed: {error}"
        ) from error