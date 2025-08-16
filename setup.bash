#cd into slack-rag/

pip install -r api/requirements.txt
pip install -r slack_bot/requirements.txt

export OLLAMA_HOST="http://127.0.0.1:11434"
export GEN_MODEL="llama3:instruct"
export EMBED_MODEL="nomic-embed-text"
export DATA_DIR="$(pwd)/data"
export CHROMA_DIR="$(pwd)/chroma_local"
export CHROMA_TELEMETRY_IMPLEMENTATION=none

ollama pull llama3:instruct
ollama pull nomic-embed-text





python api/ingest.py


uvicorn api.app:app --host 0.0.0.0 --port 8000


python slack_bot/bot.py