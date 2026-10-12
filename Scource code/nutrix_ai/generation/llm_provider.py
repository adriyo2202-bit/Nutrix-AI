import os
import json
import urllib.request
import urllib.error
import ssl
import logging

logger = logging.getLogger(__name__)



class LLMProvider:
    """
    Abstractions for the Local LLM (Ollama).
    """
    def __init__(self):
        self.url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1/chat/completions")
        self.model = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")

    def generate_stream(self, messages):
        import requests
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5,
            "stream": True
        }
        
        try:
            in_thinking = False
            with requests.post(self.url, json=data, headers=headers, stream=True, timeout=300) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk['choices'][0]['delta']
                                if 'content' in delta and delta['content']:
                                    content = delta['content']
                                    if not in_thinking and "<think>" in content:
                                        parts = content.split("<think>", 1)
                                        if parts[0]:
                                            yield parts[0]
                                        in_thinking = True
                                        content = parts[1]
                                        
                                    if in_thinking:
                                        if "</think>" in content:
                                            in_thinking = False
                                            content = content.split("</think>", 1)[1]
                                        else:
                                            continue
                                            
                                    if content and not in_thinking:
                                        yield content
                            except json.JSONDecodeError:
                                continue
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTPError: {e}")
            yield "I'm having trouble connecting to my core processing unit right now."
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            yield f"An unexpected error occurred while thinking: {e}"

