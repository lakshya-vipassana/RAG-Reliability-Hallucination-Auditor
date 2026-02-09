import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATA_DIR = "data/raw_docs"
CHROMA_DIR = "storage/chroma"
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 3
