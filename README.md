# ☁️ Text Generation with Amazon Bedrock (Llama 3)

A small Python project that calls **Meta Llama 3 8B Instruct** through **Amazon Bedrock** using `boto3`. It sends a prompt to the model and prints the generated text. It's a minimal, clean example of using a foundation model on AWS without hosting any infrastructure.

---

## Table of Contents
1. [What is Amazon Bedrock?](#what-is-amazon-bedrock)
2. [Features](#features)
3. [Tech stack](#tech-stack)
4. [Project structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Setup](#setup)
7. [Usage](#usage)
8. [How it works](#how-it-works)
9. [Configuration](#configuration)
10. [Design decisions](#design-decisions)
11. [Limitations](#limitations)
12. [Troubleshooting](#troubleshooting)
13. [Cost and security notes](#cost-and-security-notes)
14. [Future improvements](#future-improvements)

---

## What is Amazon Bedrock?

**Amazon Bedrock** is AWS's managed service for using foundation models (Llama, Claude, Titan, Mistral and others) through a single API. You don't download model weights or manage GPUs: you send a request, AWS runs the model, and you pay per use. This project uses Bedrock's **runtime** API (`bedrock-runtime`) to run Meta's Llama 3 8B Instruct model.

---

## Features
- Generates text from any prompt with Llama 3 8B Instruct
- Pass your own prompt on the command line, or use the built-in default
- Correct Llama 3 chat formatting applied automatically
- Clear error messages for missing credentials or AWS errors
- Region configurable through an environment variable

---

## Tech stack

| Component | Technology | Role |
|-----------|-----------|------|
| Language | Python 3.9+ | Core language |
| AWS SDK | boto3 | Calls the Bedrock Runtime API |
| Service | Amazon Bedrock | Hosts and runs the model |
| Model | `meta.llama3-8b-instruct-v1:0` | Text generation |
| CLI tool (optional) | AWS CLI | `aws configure` to store credentials |

---

## Project structure

```
bedrock-text-generation/
├── text_generation.py   # Main script
├── requirements.txt     # Dependencies
├── .env.example         # Template for optional AWS environment variables
├── .gitignore           # Keeps credentials out of Git
└── README.md
```

---

## Prerequisites

1. **An AWS account.**
2. **Model access enabled in Bedrock.** In the AWS Console, open *Amazon Bedrock* → *Model access* and request access to **Meta Llama 3 8B Instruct**. Without this, calls fail with an access-denied error.
3. **AWS credentials** for an IAM user or role allowed to call `bedrock:InvokeModel`.
4. **A region where the model is available.** Defaults to `us-east-1`. Check the Bedrock console to confirm availability in your region.

---

## Setup

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd bedrock-text-generation
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS credentials (choose one)

**Option A: AWS CLI (recommended)**
```bash
pip install awscli        # or install the AWS CLI from AWS's website
aws configure
```
Enter your access key ID, secret access key, and default region when prompted. Credentials are stored outside the project folder.

**Option B: Environment variables**
```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1
```
On Windows PowerShell use `$env:AWS_ACCESS_KEY_ID="..."`.

> ⚠️ Never write real keys into the code or commit them to Git.

---

## Usage

**Default prompt (poem on data science students):**
```bash
python text_generation.py
```

**Your own prompt:**
```bash
python text_generation.py "Explain overfitting in simple words"
```

The generated text is printed to the terminal.

---

## How it works

```
Your prompt ─► Llama 3 chat format ─► JSON payload ─► boto3 invoke_model
                                                           │
                                              Amazon Bedrock runs Llama 3 8B
                                                           │
                          JSON response ◄──────────────────┘
                                │
                  response["generation"] printed
```

1. **Client:** `boto3.client("bedrock-runtime")` creates a connection to Bedrock in the chosen region, using your configured credentials.
2. **Prompt formatting:** Llama 3 Instruct expects special tokens that mark roles:
   - `<|begin_of_text|>` starts the prompt
   - `<|start_header_id|>user<|end_header_id|>` marks the user message
   - `<|eot_id|>` ends the message
   - `<|start_header_id|>assistant<|end_header_id|>` tells the model to answer next
3. **Payload:** the formatted prompt and generation settings are serialized to JSON.
4. **Invocation:** `invoke_model` sends the request with the model ID and returns a streaming body.
5. **Parsing:** the body is read and decoded as JSON, and the text is in the `generation` field.
6. **Errors:** AWS errors (access denied, throttling, wrong region) and credential problems are caught and shown as readable messages.

---

## Configuration

Settings in `build_payload()` and at the top of `text_generation.py`:

| Setting | Default | Effect |
|---------|---------|--------|
| `MODEL_ID` | `meta.llama3-8b-instruct-v1:0` | Which Bedrock model to call |
| `REGION` | `us-east-1` (or `AWS_REGION`) | AWS region used |
| `max_gen_len` | 512 | Maximum tokens in the reply |
| `temperature` | 0 | 0 = deterministic and focused; higher (0.5 to 1) = more creative |
| `top_p` | 1 | Nucleus sampling cutoff; lower values narrow word choices |

> Different Bedrock models use **different request and response formats**. If you change `MODEL_ID` to another model family, you must also change the payload fields and how the response is parsed. Check that model's documentation.

---

## Design decisions

- **Bedrock instead of self-hosting.** No GPUs or model downloads, and pay-per-use pricing.
- **Chat-template formatting in a function.** Llama 3 is sensitive to its special tokens, so `build_payload()` keeps formatting in one place.
- **Prompt from the command line.** Easy to experiment without editing code.
- **Credentials from the AWS credential chain.** boto3 finds credentials from the AWS CLI config, environment variables or IAM roles, so no secrets live in the code.
- **Small, single-file script.** Simple to read, run and extend.

---

## Limitations

- **Single-turn only.** There is no conversation memory, so each run is independent.
- **No streaming.** The full response arrives at once; Bedrock also supports streaming via `invoke_model_with_response_stream`.
- **Short output cap.** `max_gen_len=512` may cut off long answers.
- **Model-specific code.** The payload format only works for Llama 3 models.
- **Needs an AWS account and model access.** It can't run offline.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `AccessDeniedException` | Request model access in the Bedrock console and make sure your IAM user has `bedrock:InvokeModel` permission. |
| `NoCredentialsError` / credentials message | Run `aws configure` or set the AWS environment variables. |
| `ValidationException` about the model ID | Confirm the model is available in your region and the ID is spelled correctly. |
| `ResourceNotFoundException` / model not found | The model may not be offered in your region, or may have been retired. Check the Bedrock console for current models. |
| `ThrottlingException` | You're sending requests too fast; wait and retry. |
| Output cut off mid-sentence | Increase `max_gen_len`. |
| Odd or off-format replies | Make sure the Llama 3 special tokens in `build_payload()` are unchanged. |

---

## Cost and security notes

- **Cost:** Bedrock charges per input and output token. Small experiments are cheap, but keep an eye on usage, and set a billing alert in AWS.
- **Credentials:** use an IAM user or role with the minimum permissions needed (`bedrock:InvokeModel`), never your root account keys.
- **If a key leaks:** deactivate and rotate it immediately in the IAM console.

---

## Future improvements

- [ ] Interactive chat loop with conversation history
- [ ] Streaming responses
- [ ] Support multiple models (Claude, Titan, Mistral) behind one interface
- [ ] Use the Bedrock Converse API, which gives a uniform format across models
- [ ] Simple web UI with Streamlit
- [ ] Unit tests with a mocked Bedrock client

---

## License
Add a license of your choice (e.g., MIT) before publishing.
