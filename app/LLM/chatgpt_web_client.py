import os
import hashlib
from dotenv import load_dotenv
from openai import OpenAI
from app.utils.prompt_builder import PromptBuilder
from app.utils.web_search import web_search
from app.utils.google_search import google_search

load_dotenv()

class ChatGPTWebClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OpenAI API key not found in environment variables")

        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=self.api_key)
        self.prompt_builder = PromptBuilder()
        self.cache = {}

    def hash_question(self, question: str) -> str:
        return hashlib.sha256(question.encode("utf-8")).hexdigest()

    def ask(self, question: str):
        q_hash = self.hash_question(question)
        if q_hash in self.cache:
            print("[CACHE HIT] Returning cached answer.")
            return self.cache[q_hash]

        #duckduckgo_search
        # context = web_search(question)
        # prompt = self.prompt_builder.build_prompt(context, question, stream=False)
        # google_search
        search_results = google_search(question)
        prompt = f"Використай цю інформацію з вебу:\n{search_results}\n\nПитання: {question}\nВідповідь:"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content
        self.cache[q_hash] = answer
        return answer

    def ask_stream(self, question: str):
        #duckduckgo_search
        # context = web_search(question)
        # prompt = self.prompt_builder.build_prompt(context, question, stream=False)
        # google_search
        search_results = google_search(question)
        prompt = f"Використай цю інформацію з вебу:\n{search_results}\n\nПитання: {question}\nВідповідь:"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def preSessionConfiguration(self):
        prompt = self.prompt_builder.session_intro_prompt()

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def postCall(self):
        print("[INFO] ChatGPTWebClient does not require postCall().")
