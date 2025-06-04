import hashlib
import os
from dotenv import load_dotenv
from openai import OpenAI
from app.utils.prompt_builder import PromptBuilder
from app.utils.rag_retriever import RAGRetriever

load_dotenv()

class ChatGPTClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OpenAI API key not found in environment variables")

        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=self.api_key)
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

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )

        answer = response.choices[0].message.content
        self.cache[q_hash] = answer
        return answer

    def ask_stream(self, question: str):
        context = self.rag.retrieve_context(question)
        prompt = self.prompt_builder.build_prompt(context, question, stream=True)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except Exception as e:
            yield f"❌ Error during streaming: {str(e)}"

    def preSessionConfiguration(self):
        prompt = self.prompt_builder.session_intro_prompt()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except Exception as e:
            yield f"❌ Error in preSessionConfiguration: {str(e)}"

    def postCall(self):
        print("[INFO] ChatGPTClient does not require postCall().")
