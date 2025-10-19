import os

class Settings:
    DATA_PATH = os.getenv("DATA_PATH", "data/products.csv")
    VECTOR_INDEX_DIR = os.getenv("VECTOR_INDEX_DIR", "backend/vectorstore")
    IMAGE_MODEL_PATH = os.getenv("IMAGE_MODEL_PATH", "backend/models/resnet18_furniture.pt")
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    # Optional: Pinecone (or other) config if you choose to use a hosted vector DB
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "ikarus-products")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional for GenAI descriptions via LangChain

settings = Settings()
