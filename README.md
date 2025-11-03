# Auto-Generation System: A Deep Dive into Code-to-Doc AI
This project develops an advanced, multi-modal AI system designed to solve the critical developer problem of maintaining up-to-date and informative documentation. The core service is the **Automatic README Generation AI**, which transforms raw GitHub code into structured Markdown documentation. This feature is integrated into a larger career management platform, aiming to streamline workflow convenience and enhance job-seeking capabilities.

### The Challenge of Documentation & Token Efficiency

Manually documenting extensive codebases is tedious and error-prone. Furthermore, feeding entire code files to Large Language Models (LLMs) is prohibitively expensive due to high token consumption.

**Our Solution**: Implement an **Abstract Syntax Tree (AST) Analysis Pipeline** to pre-process code, drastically reducing the token budget while maximizing the information density of the input prompt.

---

### 📂 Branch/Commit Naming Convention

**Examples:**

* `feat/login-api`
* `fix/comment-delete-bug`
* `test/user-service-test`

**Type List:**

| Type       | Description                                         |
| ---------- | --------------------------------------------------- |
| `feat`     | Add a new feature                                   |
| `fix`      | Fix a bug                                           |
| `refactor` | Improve code quality without changing functionality |
| `test`     | Add or modify test code                             |
| `hotfix`   | Apply an urgent fix                                 |

---

## 1. Demonstration and Visual Context

### 1-1. Project Workflow Demonstration

This video showcases the end-to-end functionality, from inputting a GitHub repository URL to receiving the final, structured Markdown README file.

![454307305-62f04eb9-9979-45bb-9dc8-b3bd6ab2faf2](https://github.com/user-attachments/assets/f1a32750-3f94-4147-9d5a-cf1624112a6e)


### 1-2. AST Analysis Visual

The image below illustrates the concept of Abstract Syntax Trees, which is central to our token optimization strategy.

---

## 2. Technical Architecture and Model Selection

The system utilizes a specialized combination of models for task-specific performance, leveraging both local GPU infrastructure and external, high-throughput APIs.

### 2-1. The README Generation Pipeline (QwenCoder + AST)

The README generation process is engineered for efficiency and code comprehension:

| Stage                      | Process                                                                                                                                                                | Key Technology / Model              | Rationale                                                                              |
| :------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------- | :------------------------------------------------------------------------------------- |
| **I. Code Ingestion**      | Retrieve target code files from a linked GitHub repository.                                                                                                            | GitHub API Integration              | Ensures access to the most current codebase.                                           |
| **II. Token Optimization** | Convert raw code (e.g., Python) into an **Abstract Syntax Tree (AST)**. **Only critical nodes (function definitions, library imports, key logic flow)** are extracted. | AST Parser (`libcst` or equivalent) | **CRITICAL for cost reduction and focus.** Reduces LLM input token count by up to 90%. |
| **III. Generation**        | The processed AST metadata is transformed into a concise, context-rich prompt and fed to the LLM.                                                                      | **QwenCoder Model**                 | Selected for superior performance, as detailed below.                                  |

---

### 2-2. Model Selection Rationale (QwenCoder)

The QwenCoder model was chosen as the primary engine for README generation based on stringent performance criteria:

| Criterion                | QwenCoder Performance | Justification                                                                              |
| :----------------------- | :-------------------- | :----------------------------------------------------------------------------------------- |
| **Code Understanding**   | **High**              | Proven ability to grasp complex code structure and context.                                |
| **Multilingual Support** | **High**              | Essential for processing code in diverse programming languages.                            |
| **MultiPL-E Score**      | **High Ranking**      | Verifies strong performance on the **Multi-Programming Language Evaluation** benchmark.    |
| **McEval Score**         | **High Ranking**      | Verifies superior performance on the **Massively Multilingual Code Evaluation** benchmark. |


<img width="1153" height="707" alt="image" src="https://github.com/user-attachments/assets/b6f5db2d-a07f-4edc-88ad-3f5842f67603" />


---

### 2-3. Code Analysis for Tagging (Ensemble Learning)

A separate ensemble system analyzes repository content to recommend technical tags, prioritizing accuracy and diversity.

| Model / System           | Role                   | Execution Method                    | Rationale                                                                |
| :----------------------- | :--------------------- | :---------------------------------- | :----------------------------------------------------------------------- |
| **Gemini-thinking**      | Inference & Reasoning  | **Multi-threaded API Call**         | Utilized for strong reasoning and structural interpretation.             |
| **Qwen-coder-32b**       | Code-Specific Analysis | **Multi-threaded API Call**         | Provides robust, code-centric analysis.                                  |
| **llama-versatile**      | Auxiliary Analysis     | **Multi-threaded API Call**         | Contributes diverse perspectives and maintains high throughput.          |
| **Ensemble Aggregation** | Final Decision         | **Bagging Technique (JSON Output)** | Combines results (majority vote) to significantly boost tag reliability. |

---

## 3. Environment Setup and Execution

### 3-1. Development Requirements

| Dependency           | Purpose                                                              | Installation                                                                  |
| :------------------- | :------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| **Python**           | Core runtime environment.                                            | `Python 3.10+`                                                                |
| **Libraries / SDKs** | Required for LLM inference, AST analysis, and external model access. | `pip install -r requirements.txt` (See `requirements.txt` for exact versions) |

> ⚠️ **Note:** For exact library versions, please refer to the [`requirements.txt`](./requirements.txt) file included in this project.

---

### 3-2. API Keys Configuration

To ensure secure access to external LLM services, create a file named **`.env`** in the project's root directory:

```text
# --- External AI Service Credentials ---

# Google AI (Gemini) API Key for the Code Analysis Ensemble
# Used for its robust inference capabilities.
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# Groq API Key for the Code Analysis Ensemble
# Used for its high-speed inference in multi-model parallel processing.
GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"

# --- Local Server Configuration ---

# URL for the local vLLM server hosting the BART model (for summarization feature)
BART_VLLM_SERVER_URL="http://127.0.0.1:8000/v1/completions"
```

---

### 3-3. Execution Steps

1. **Install Dependencies**: Install all required packages using `pip`.
```bash
# You can use Anaconda/Miniconda or venv
conda create -n [ENVIRONMENT_NAME] python=3.10
conda activate [ENVIRONMENT_NAME]
pip install -r requirements.txt
```
2. **API Setup**: Configure the `.env` file with necessary API keys (Section 3-2).
3. **Run vLLM Server**: (If the Summarization feature is active) Start the local GPU server hosting the BART model via vLLM.
4. **Execute Generation Script**: Run the main Python script, providing the GitHub repository URL as input.

```bash
# Example: Running the main README generation script
python run_readme_generator.py --repo_url "https://github.com/user/project"
```
