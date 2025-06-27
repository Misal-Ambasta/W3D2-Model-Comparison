# Model Comparison CLI Tool

## Overview
This command-line tool allows users to compare Base, Instruct, and Fine-tuned models from OpenAI and Ollama. It supports interactive queries, model selection, and visualizes token usage and context window length.

## Models Supported
- **Base Model**: mistral:latest (via Ollama)
- **Instruct Model**: gpt-3.5-turbo (via OpenAI API)
- **Fine-tuned Model**: openhermes:latest (via Ollama)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd W3D2-Model-Comparison
```

### 2. Create and Activate Conda Environment
```bash
conda activate rlhf310
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and Setup Ollama
```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Pull required models
ollama pull mistral:latest
ollama pull openhermes:latest
```

### 5. Configure API Keys
- Copy `.env.example` to `.env` and fill in your OpenAI API key.

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

### Running the CLI Tool
```bash
python cli.py
```

### Available Modes

#### 1. Manual Mode - Comparative Query
- Enter your own prompt
- The tool will automatically run your query through all three models (base, instruct, fine-tuned)
- Prints each model's response and summary
- **Generates comparative images**:
  - `token_usage_comparison.png` (bar chart comparing prompt/response tokens for all models)
  - `context_window_comparison.png` (bar chart comparing context window lengths for all models)
- **Appends the comparison to `comparisons.md` in bullet-point format, including prompt/response tokens for each model**
- Best for: Side-by-side comparison of all models for a single query

#### 2. Auto Mode - Batch Comparison
- Runs 5 predefined diverse prompts through all 3 models
- **Does NOT generate comparative images**
- **Appends each comparison to `comparisons.md` in bullet-point format, including prompt/response tokens for each model**
- Automatically generates `comparisons.md` with results
- Includes summary table and model analysis
- Best for: Comprehensive model comparison and documentation

### Output Files
- **Manual Mode**: PNG files showing token usage and context window length comparisons for your query
- **Auto Mode**: Only the `comparisons.md` file with detailed comparison results (no images)
- **comparisons.md**: Contains all comparisons (manual and auto), with each entry showing the query, datetime, and for each model: the response, prompt tokens, and response tokens. The latest comparison appears at the top.

## Example Outputs

### Manual or Auto Mode (comparisons.md entry)
```
## [2025-06-27 11:40:57] Manual Mode
**Query:** Create a step-by-step guide for making a sandwich.

- **Base (mistral:latest, Ollama):**
  [Error: llama runner process has terminated: error loading model: unable to allocate CUDA0 buffer (status code: 500)]
  _Prompt tokens: 10, Response tokens: 0_
- **Instruct (gpt-3.5-turbo, OpenAI):**
  Step 1: Gather all the ingredients you will need for your sandwich. ...
  _Prompt tokens: 10, Response tokens: 45_
- **Fine-tuned (openhermes:latest, Ollama):**
  [Error: llama runner process has terminated: error loading model: unable to allocate CUDA0 buffer (status code: 500)]
  _Prompt tokens: 10, Response tokens: 0_

---
```

### Manual Mode (images)
```
[Visualization] Token usage comparison image saved to: token_usage_comparison.png
[Visualization] Context window comparison image saved to: context_window_comparison.png
```

### Auto Mode
```
=== Auto Comparison Mode ===

Running predefined prompts through all models...
[Prompt 1/5]: Explain quantum computing in simple terms.
  Testing Base (mistral:latest, Ollama)...
  Testing Instruct (gpt-3.5-turbo, OpenAI)...
  Testing Fine-tuned (openhermes:latest, Ollama)...

[Success] comparisons.md updated with all auto mode results!
# (No images are generated in Auto Mode)
```

## Notes on Ollama and GPU/VRAM Requirements
- Large models like `mistral:latest` and `openhermes:latest` may require more than 4GB VRAM to run on GPU.
- If you encounter errors such as `unable to allocate CUDA0 buffer`, your GPU may not have enough memory for the model.
- In such cases, try:
  - Closing other GPU-intensive applications
  - Using a smaller or quantized model (if available)
  - Allowing Ollama to run in CPU mode (will use system RAM, but may be slower)
- You can check your GPU usage with `nvidia-smi` (on Windows, use Command Prompt or PowerShell).

## Troubleshooting
- If you see errors related to OpenAI API, ensure your API key is correct and you have access to `gpt-3.5-turbo`.
- For Ollama errors, check your system's RAM and VRAM availability.
- For further help, consult the [Ollama documentation](https://ollama.ai) and [OpenAI Python library migration guide](https://github.com/openai/openai-python/discussions/742).