import os
from pathlib import Path

from langchain.tools import BaseTool

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
STORAGE_DIR = Path(__file__).parent.parent / "storage"


class KnowledgeBaseTool(BaseTool):
    name: str = "search_knowledge_base"
    description: str = (
        "Search the local knowledge base with hybrid keyword + vector retrieval. "
        "Use when the user asks about documents or information stored locally. "
        "Input: a search query string."
    )

    def _run(self, query: str) -> str:
        if not KNOWLEDGE_DIR.exists() or not any(KNOWLEDGE_DIR.rglob("*")):
            return "Knowledge base is empty. Add PDF, Markdown, or TXT files to knowledge/."

        try:
            from llama_index.core import (
                SimpleDirectoryReader,
                StorageContext,
                VectorStoreIndex,
                load_index_from_storage,
            )
            from llama_index.core import Settings
            from llama_index.core.retrievers import QueryFusionRetriever
            from llama_index.embeddings.openai import OpenAIEmbedding
            from llama_index.retrievers.bm25 import BM25Retriever
        except ImportError as e:
            return f"Missing dependency: {e}. Run: pip install llama-index-core llama-index-retrievers-bm25 llama-index-embeddings-openai"

        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv("MODEL_API_KEY", "sk-placeholder"),
            api_base=os.getenv("MODEL_BASE_URL"),
        )
        Settings.llm = None  # retrieval only, no LLM needed

        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        index_path = STORAGE_DIR / "llama_index"

        if index_path.exists():
            ctx = StorageContext.from_defaults(persist_dir=str(index_path))
            index = load_index_from_storage(ctx)
        else:
            docs = SimpleDirectoryReader(
                str(KNOWLEDGE_DIR), recursive=True, required_exts=[".pdf", ".md", ".txt"]
            ).load_data()
            index = VectorStoreIndex.from_documents(docs)
            index.storage_context.persist(persist_dir=str(index_path))

        vector_retriever = index.as_retriever(similarity_top_k=3)
        all_nodes = list(index.docstore.docs.values())
        bm25_retriever = BM25Retriever.from_defaults(nodes=all_nodes, similarity_top_k=3)

        retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=5,
            num_queries=1,  # no LLM query expansion
            use_async=False,
        )

        results = retriever.retrieve(query)
        if not results:
            return "No relevant documents found."

        return "\n\n---\n\n".join(
            f"**Source:** {r.metadata.get('file_name', 'unknown')}\n{r.text}"
            for r in results
        )

    async def _arun(self, query: str) -> str:
        return self._run(query)
