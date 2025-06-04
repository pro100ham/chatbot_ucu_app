import requests
import hashlib
import os
from dotenv import load_dotenv
from app.utils.prompt_builder import PromptBuilder
from app.utils.rag_retriever import RAGRetriever

load_dotenv()

class OllamaClient:
    def __init__(self):
        env_mode = os.getenv("ACTIVE_ENV", "local")
        self.MODEL_NAME = os.getenv("MODEL_NAME", "mistral")
        self.url = (
            os.getenv("DOCKER_OLLAMA_URL") + "/generate"
            if env_mode == "docker"
            else os.getenv("LOCAL_OLLAMA_URL") + "/generate"
        )

        if not self.url:
            raise ValueError("❌ Ollama URL is not defined. Check your .env configuration.")

        self.prompt_builder = PromptBuilder()
        self.rag = RAGRetriever()
        self.cache = {}

    def hash_question(self, question: str) -> str:
        return hashlib.sha256(question.encode("utf-8")).hexdigest()

    def ask(self, question: str):
        q_hash = self.hash_question(question)
        if q_hash in self.cache:
            print("[CACHE HIT] Returning cached answer.")
            return self.cache[q_hash]

        context = self.rag.retrieve_context(question)
        prompt = self.prompt_builder.build_prompt(context, question, stream=False)

        payload = {
            "model": self.MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        answer = response.json()["response"]
        self.cache[q_hash] = answer
        return answer

    def ask_stream(self, question: str):
        context = self.rag.retrieve_context(question)
        prompt = self.prompt_builder.build_prompt(context, question, stream=True)

        payload = {
            "model": self.MODEL_NAME,
            "prompt": prompt,
            "stream": True
        }

        with requests.post(self.url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue
                yield line

    def postCall(self):
        try:
            env_mode = os.getenv("ACTIVE_ENV", "local")
            MODEL_NAME = os.getenv("MODEL_NAME", "mistral")

            payload = {"name": MODEL_NAME}
            url = os.getenv("DOCKER_OLLAMA_URL") + "/pull" if env_mode == "docker" else os.getenv("LOCAL_OLLAMA_URL") + "/pull"

            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"✅ Model '{MODEL_NAME}' pulled successfully")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to pull model '{MODEL_NAME}': {e}")

    def preSessionConfiguration(self):
        prompt = self.prompt_builder.session_intro_prompt()

        payload = {
            "model": self.MODEL_NAME,
            "prompt": prompt,
            "stream": True
        }

        with requests.post(self.url, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue
                yield line
