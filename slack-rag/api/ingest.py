import os, asyncio
from pathlib import Path
from raglib import add_documents, SUPPORTED_EXTS, DATA_DIR

async def main():
    paths = [p for p in Path(DATA_DIR).rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    if not paths:
        print(f"No documents found in {DATA_DIR}. Add .txt/.md/.pdf and rerun.")
        return
    out = await add_documents(paths)
    print(out)

if __name__ == "__main__":
    asyncio.run(main())
