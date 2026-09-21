import re
import argparse
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


PROJECT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = PROJECT_DIR / "data" / "knowledge"
DATABASE_DIR = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "f1_driver_knowledge"


def get_collection():
    client = chromadb.PersistentClient(path=str(DATABASE_DIR))

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DefaultEmbeddingFunction(),
    )


def read_metadata(header: str, field: str) -> str:
    prefix = f"{field}:"

    for line in header.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()

    raise ValueError(f"Missing '{field}:' in a knowledge document.")


def build_index():
    files = sorted(KNOWLEDGE_DIR.glob("*.md"))

    if not files:
        raise ValueError(f"No Markdown files found in {KNOWLEDGE_DIR}")

    ids = []
    documents = []
    metadatas = []

    for file in files:
        text = file.read_text(encoding="utf-8-sig").strip()

        # Each ## heading starts a separate searchable passage.
        sections = text.split("\n## ")
        header = sections[0]

        title = header.splitlines()[0].removeprefix("# ").strip()
        source = read_metadata(header, "Source")
        checked_on = read_metadata(header, "Checked on")
        coverage = read_metadata(header, "Coverage")

        if len(sections) < 2:
            raise ValueError(f"{file.name} has no ## section headings.")

        for number, section in enumerate(sections[1:]):
            heading, separator, body = section.partition("\n")

            if not separator or not body.strip():
                raise ValueError(f"Empty section in {file.name}: {heading}")

            # Include the driver's name so every passage has context.
            passage = f"{title}\n{heading.strip()}\n{body.strip()}"

            ids.append(f"{file.name}:{number}")
            documents.append(passage)
            metadatas.append(
                {
                    "title": title,
                    "section": heading.strip(),
                    "source": source,
                    "checked_on": checked_on,
                    "coverage": coverage,
                    "filename": file.name,
                }
            )

    collection = get_collection()

    # Insert new passages or update passages with the same IDs.
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    # Remove old generated passages if source files were shortened
    # or removed. This does not modify the Markdown files.
    current_ids = set(ids)
    stored_ids = collection.get(include=[])["ids"]
    stale_ids = [
        record_id for record_id in stored_ids
        if record_id not in current_ids
    ]

    if stale_ids:
        collection.delete(ids=stale_ids)

    print(f"Indexed {len(files)} files into {collection.count()} passages.")
    print(f"Database location: {DATABASE_DIR}")


def retrieve(question: str, limit: int = 4) -> list[dict]:
    collection = get_collection()

    if limit < 1:
        raise ValueError("The retrieval limit must be at least 1.")

    total = collection.count()

    if total == 0:
        raise ValueError(
            "The index is empty. Run: uv run python rag.py --index"
        )

    driver_patterns = {
        "Fernando Alonso": r"\balonso\b",
        "Lewis Hamilton": r"\bhamilton\b",
        "Max Verstappen": r"\bverstappen\b",
    }

    matched_drivers = [
        name
        for name, pattern in driver_patterns.items()
        if re.search(pattern, question, flags=re.IGNORECASE)
    ]

    filters = {}
    available = total

    if len(matched_drivers) == 1:
        filters["where"] = {"title": matched_drivers[0]}

        matching_records = collection.get(
            include=[],
            **filters,
        )
        available = len(matching_records["ids"])

    if available == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(limit, available),
        include=["documents", "metadatas"],
        **filters,
    )

    return [
        {"text": text, "metadata": metadata}
        for text, metadata in zip(
            results["documents"][0],
            results["metadatas"][0],
        )
    ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--index", action="store_true")
    action.add_argument("--query", type=str)
    args = parser.parse_args()

    if args.index:
        build_index()
    else:
        for number, passage in enumerate(retrieve(args.query), start=1):
            print(f"\n--- Retrieved passage {number} ---")
            print(passage["text"])
            print(f"Source: {passage['metadata']['source']}")
            print(f"Coverage: {passage['metadata']['coverage']}")