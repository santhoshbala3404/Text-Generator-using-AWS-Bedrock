"""Generate text with Meta Llama 3 8B Instruct on Amazon Bedrock.

Run:
    python text_generation.py
    python text_generation.py "Explain overfitting in simple words"
"""
import json
import os
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError

MODEL_ID = "meta.llama3-8b-instruct-v1:0"
REGION = os.getenv("AWS_REGION", "us-east-1")

DEFAULT_PROMPT = "Write a poem on data science and machine learning students."


def build_payload(user_prompt: str) -> dict:
    """Wrap the prompt in Llama 3's chat format and set generation parameters."""
    formatted_prompt = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    return {
        "prompt": formatted_prompt,
        "max_gen_len": 512,   # maximum tokens to generate
        "temperature": 0,     # 0 = deterministic, higher = more creative
        "top_p": 1,
    }


def generate_text(user_prompt: str) -> str:
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=REGION)

    response = bedrock.invoke_model(
        body=json.dumps(build_payload(user_prompt)),
        modelId=MODEL_ID,
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response["body"].read())
    return response_body["generation"]


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT
    try:
        print(generate_text(prompt))
    except ClientError as e:
        raise SystemExit(f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        raise SystemExit(
            f"Could not call AWS ({e}). Check your credentials with 'aws configure'."
        )
