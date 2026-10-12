import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath("Scource code"))

from nutrix_ai.generation.llm_provider import LLMProvider

def main():
    llm = LLMProvider()
    messages = [{"role": "user", "content": "What is protein?"}]
    print("Testing LLM Provider...")
    try:
        generator = llm.generate_stream(messages)
        for chunk in generator:
            sys.stdout.buffer.write(chunk.encode('utf-8'))
        print("\n\nDone.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
