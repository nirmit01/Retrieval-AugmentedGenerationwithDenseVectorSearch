# rag_pipeline.py
# Handles chunking, embeddings, vector store, and RAG Q&A
# Using EXACT code from working Colab notebook

import os
import faiss
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from urllib.parse import urlparse, parse_qs
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# ---------------------------------------------------------------------------
# Module-level singletons (loaded once, reused across requests)
# ---------------------------------------------------------------------------

_embeddings = None
_llm_model = None

# In-memory store: maps video_id → FAISS vector store
_vector_stores: dict = {}


def get_youtube_id(url: str) -> str | None:
    """Extract video ID from YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            return qs.get("v", [None])[0]
        for prefix in ("/embed/", "/v/"):
            if parsed.path.startswith(prefix):
                return parsed.path.split(prefix)[-1]
    return None


def _get_embeddings():
    """Lazy-load the embedding model (same as notebook)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            encode_kwargs={'batch_size': 32}
        )
    return _embeddings


def _get_llm_model():
    """Lazy-load the HuggingFace LLM (same model as notebook)."""
    global _llm_model
    if _llm_model is None:
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not hf_token:
            # Try to get from environment directly like notebook does
            hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN", os.environ.get("HF_TOKEN", ""))

        if not hf_token:
            raise EnvironmentError("HUGGINGFACEHUB_API_TOKEN is not set in environment.")

        llm = HuggingFaceEndpoint(
            repo_id="openai/gpt-oss-120b",
            task="text-generation",
            huggingfacehub_api_token=hf_token,
        )
        _llm_model = ChatHuggingFace(llm=llm)
    return _llm_model


# ---------------------------------------------------------------------------
# RAG prompt (exact template from notebook)
# ---------------------------------------------------------------------------

RAG_PROMPT = PromptTemplate(
    template="""
    You are a helpful assistant.
    Answer only from the provided transcript context.
    If the context is insufficient, just say you don't know.

    {context}
    Question : {question}
    """,
    input_variables=['context', 'question']
)


def build_vector_store(video_id: str, transcript: str):
    """
    Chunk the transcript → embed → store in FAISS (exact method from notebook).
    Uses SemanticChunker and HNSW index like notebook.
    """
    embeddings = _get_embeddings()

    # Semantic Chunking (exact from notebook)
    semantic_splitter = SemanticChunker(embeddings)
    chunks = semantic_splitter.create_documents([transcript])

    print(f"Created {len(chunks)} semantic chunks.")

    # Define dimensions for all-MiniLM-L6-v2
    embedding_dim = 384

    # m is the number of bi-directional links created for every new element during HNSW insertion
    m = 32

    # Build the HNSW index (exact from notebook)
    hnsw_index = faiss.IndexHNSWFlat(embedding_dim, m)

    # Wrap the raw FAISS index in LangChain (exact from notebook)
    vector_store = FAISS(
        embedding_function=embeddings,
        index=hnsw_index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    # Ingest the semantic chunks (exact from notebook)
    vector_store.add_documents(chunks)

    _vector_stores[video_id] = vector_store
    return vector_store


def get_vector_store(video_id: str):
    """Retrieve a previously built vector store by video ID."""
    return _vector_stores.get(video_id)


def format_docs(retrieved_docs):
    """Concatenate retrieved document chunks."""
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text


def answer_question(video_id: str, question: str) -> str:
    """
    RAG pipeline (exact chain from notebook).
    """
    vector_store = get_vector_store(video_id)
    if vector_store is None:
        raise ValueError(f"No vector store found for video '{video_id}'. Process it first.")

    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={"k": 4})

    model = _get_llm_model()
    parser = StrOutputParser()

    # Exact chain from notebook
    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })

    main_chain = parallel_chain | RAG_PROMPT | model | parser
    return main_chain.invoke(question)


def generate_summary(transcript: str) -> str:
    """Generate a summary using the LLM."""
    model = _get_llm_model()
    parser = StrOutputParser()

    # Simple prompt for summary
    SUMMARY_PROMPT = PromptTemplate(
        template="""
        You are a helpful assistant. Below is a transcript from a YouTube video.
        Please provide a clear, structured summary covering:
        - Main topic
        - Key points (bullet points)
        - Important conclusions

        Transcript:
        {transcript}
        """,
        input_variables=['transcript']
    )

    # Limit transcript length
    truncated = transcript[:4000] if len(transcript) > 4000 else transcript
    final_prompt = SUMMARY_PROMPT.invoke({"transcript": truncated})

    answer = model.invoke(final_prompt)
    return parser.invoke(answer)