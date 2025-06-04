import json
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer
import os


class RAGRetriever:
    def __init__(self, index_path="app/documents/rag_index.faiss", chunks_path="app/documents/rag_chunks.json"):
        with open(chunks_path, encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        self.index = faiss.read_index(index_path)
        self.vectorizer = TfidfVectorizer().fit(self.chunks)
        self.tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")

    def retrieve_context(self, question: str, top_k: int = 3, max_tokens: int = 2048) -> str:
        # Embedding-based retrieval
        question_vector = self.model.encode([question], convert_to_numpy=True)
        distances, indices = self.index.search(question_vector, top_k)
        embedding_chunks = [self.chunks[i] for i in indices[0] if i != -1]

        # Keyword-based retrieval (TF-IDF)
        tfidf_matrix = self.vectorizer.transform(self.chunks)
        tfidf_q = self.vectorizer.transform([question])
        tfidf_scores = cosine_similarity(tfidf_q, tfidf_matrix).flatten()
        top_indices_tfidf = tfidf_scores.argsort()[-top_k:][::-1]
        keyword_chunks = [self.chunks[i] for i in top_indices_tfidf]

        # Combine and deduplicate
        combined_chunks = list(dict.fromkeys(embedding_chunks + keyword_chunks))
        context = "\n\n".join(combined_chunks)
        return self.truncate_by_tokens(context, max_tokens)

    def truncate_by_tokens(self, text: str, max_tokens: int = 2048) -> str:
        tokens = self.tokenizer.encode(text, add_special_tokens=False, truncation=True, max_length=max_tokens)
        return self.tokenizer.decode(tokens[:max_tokens], skip_special_tokens=True)
