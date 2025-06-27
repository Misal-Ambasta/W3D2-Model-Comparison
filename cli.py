import questionary
import sys
import os
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from openai import OpenAI
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import ollama
from datetime import datetime

MODEL_TYPES = [
    {"name": "Base (mistral:latest, Ollama)", "value": "base"},
    {"name": "Instruct (gpt-3.5-turbo, OpenAI)", "value": "instruct"},
    {"name": "Fine-tuned (openhermes:latest, Ollama)", "value": "finetuned"},
]

MODEL_SUMMARIES = {
    "base": "Mistral 7B is a base, pre-trained language model from Mistral AI, available via Ollama. It is not instruction-tuned or fine-tuned for specific tasks.",
    "instruct": "GPT-3.5-turbo is OpenAI's instruction-tuned model, fine-tuned to follow instructions and provide helpful, safe responses.",
    "finetuned": "OpenHermes 7B is a fine-tuned model based on Mistral 7B, trained on instruction-following datasets for improved task performance.",
}

# Predefined prompts for auto mode
PREDEFINED_PROMPTS = [
    "Explain quantum computing in simple terms.",
    "Write a short poem about artificial intelligence.",
    "What are the main differences between machine learning and deep learning?",
    "Create a step-by-step guide for making a sandwich.",
    "Analyze the pros and cons of remote work."
]

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_tokens(model_type, text):
    # Simplified token counting - for Ollama models, we'll use word count as approximation
    if model_type == "instruct":
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(enc.encode(text))
        except ImportError:
            return len(text.split())
    else:
        # For Ollama models, use word count as approximation
        return len(text.split())

def get_context_window_length(model_type):
    if model_type == "base":
        return 8192  # Mistral 7B context window
    elif model_type == "instruct":
        return 4096  # GPT-3.5-turbo context window
    else:
        return 8192  # OpenHermes 7B context window

def plot_and_save_token_usage(prompt, response, model_type, out_path):
    prompt_tokens = count_tokens(model_type, prompt)
    response_tokens = count_tokens(model_type, response)
    labels = ['Prompt', 'Response']
    values = [prompt_tokens, response_tokens]
    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color=['#4F81BD', '#C0504D'])
    plt.title('Token Usage')
    plt.ylabel('Tokens')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_and_save_context_window(model_type, out_path):
    context_length = get_context_window_length(model_type)
    plt.figure(figsize=(6,2))
    plt.barh(['Context Window'], [context_length], color='#9BBB59')
    plt.title('Context Window Length')
    plt.xlabel('Tokens')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def generate_response(model_type, prompt):
    if model_type == "base":
        response = ollama.chat(model='mistral:latest', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()
    elif model_type == "instruct":
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    elif model_type == "finetuned":
        response = ollama.chat(model='openhermes:latest', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()
    else:
        return "[Error] Unknown model type."

def prepend_to_comparisons_md(new_entry):
    try:
        with open('comparisons.md', 'r', encoding='utf-8') as f:
            existing = f.read()
    except FileNotFoundError:
        existing = ''
    with open('comparisons.md', 'w', encoding='utf-8') as f:
        f.write(new_entry + '\n---\n' + existing)

def format_comparison_entry(query, results, mode):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"## [{timestamp}] {mode} Mode\n**Query:** {query}\n\n"
    for r in results:
        entry += f"- **{r['model']}:**\n  {r['response']}\n  _Prompt tokens: {r['prompt_tokens']}, Response tokens: {r['response_tokens']}_\n"
    return entry

def run_manual_mode():
    print("\n=== Manual Comparison Mode ===\n")
    try:
        query = questionary.text("Enter your query:").ask()
        if not query or not query.strip():
            print("[Error] Query cannot be empty.")
            return

        results = []
        for model_info in MODEL_TYPES:
            model_name = model_info["name"]
            model_value = model_info["value"]
            print(f"\n[Info] Running for: {model_name} (internal: {model_value})")
            print(f"[Model Summary]\n{MODEL_SUMMARIES[model_value]}\n")
            print("[Generating response...]")
            try:
                response = generate_response(model_value, query)
                print(f"[Model Response]\n{response}\n")
                results.append({
                    'model': model_name,
                    'model_value': model_value,
                    'response': response,
                    'prompt_tokens': count_tokens(model_value, query),
                    'response_tokens': count_tokens(model_value, response)
                })
            except Exception as e:
                print(f"[Error] Failed to generate response for {model_name}: {e}")
                results.append({
                    'model': model_name,
                    'model_value': model_value,
                    'response': f"[Error: {e}]",
                    'prompt_tokens': 0,
                    'response_tokens': 0
                })

        # Comparative visualization for token usage
        try:
            labels = [r['model'] for r in results]
            prompt_tokens = [r['prompt_tokens'] for r in results]
            response_tokens = [r['response_tokens'] for r in results]
            x = range(len(labels))
            plt.figure(figsize=(8,5))
            plt.bar(x, prompt_tokens, width=0.4, label='Prompt Tokens', align='center', color='#4F81BD')
            plt.bar(x, response_tokens, width=0.4, label='Response Tokens', align='edge', color='#C0504D')
            plt.xticks(x, labels, rotation=15)
            plt.ylabel('Tokens')
            plt.title('Token Usage Comparison')
            plt.legend()
            plt.tight_layout()
            token_img = f"token_usage_comparison.png"
            plt.savefig(token_img)
            plt.close()
            print(f"[Visualization] Token usage comparison image saved to: {token_img}")
        except Exception as e:
            print(f"[Error] Failed to generate token usage comparison image: {e}")

        # Comparative visualization for context window
        try:
            context_lengths = [get_context_window_length(r['model_value']) for r in results]
            plt.figure(figsize=(8,2))
            plt.barh(labels, context_lengths, color='#9BBB59')
            plt.xlabel('Tokens')
            plt.title('Context Window Length Comparison')
            plt.tight_layout()
            context_img = f"context_window_comparison.png"
            plt.savefig(context_img)
            plt.close()
            print(f"[Visualization] Context window comparison image saved to: {context_img}")
        except Exception as e:
            print(f"[Error] Failed to generate context window comparison image: {e}")

        # Update comparisons.md
        entry = format_comparison_entry(query, results, mode="Manual")
        prepend_to_comparisons_md(entry)
        print("[Info] Comparison results have been added to comparisons.md.")
    except KeyboardInterrupt:
        print("\n[Cancelled] Exiting manual mode.")

def run_auto_mode():
    print("\n=== Auto Comparison Mode ===\n")
    print("Running predefined prompts through all models...")
    
    for i, prompt in enumerate(PREDEFINED_PROMPTS, 1):
        print(f"\n[Prompt {i}/5]: {prompt}")
        results = []
        for model_info in MODEL_TYPES:
            model_name = model_info["name"]
            model_value = model_info["value"]
            print(f"  Testing {model_name}...")
            try:
                response = generate_response(model_value, prompt)
                results.append({
                    'model': model_name,
                    'model_value': model_value,
                    'response': response,
                    'prompt_tokens': count_tokens(model_value, prompt),
                    'response_tokens': count_tokens(model_value, response)
                })
            except Exception as e:
                print(f"    [Error] Failed for {model_name}: {e}")
                results.append({
                    'model': model_name,
                    'model_value': model_value,
                    'response': f"[Error: {e}]",
                    'prompt_tokens': 0,
                    'response_tokens': 0
                })
        # Update comparisons.md for each prompt
        entry = format_comparison_entry(prompt, results, mode="Auto")
        prepend_to_comparisons_md(entry)
    print(f"\n[Success] comparisons.md updated with all auto mode results!")

def main():
    print("\n=== Model Comparison CLI Tool ===\n")
    
    try:
        mode = questionary.select(
            "Choose comparison mode:",
            choices=[
                {"name": "Manual Mode - Interactive single query", "value": "manual"},
                {"name": "Auto Mode - Batch comparison with predefined prompts", "value": "auto"}
            ]
        ).ask()
        
        if mode == "manual":
            run_manual_mode()
        elif mode == "auto":
            run_auto_mode()
        else:
            print("[Error] Invalid mode selection.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n[Cancelled] Exiting CLI.")
        sys.exit(0)

if __name__ == "__main__":
    main() 