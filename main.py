import numpy as np
import json
import os
import sys
import re

# Add the project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
from embeddings.embedder import Embedder
from vector_store.faiss_handler import FAISSHandler
from llm.sgllm import SuggestionGenerator
from nat.nat_filler import NATFiller
from rich.console import Console
from rich.panel import Panel
from typing import List, Dict, Tuple


# --- Constants ---
NOTES_FILEPATH = "notes/user_notes.json"
SIMILARITY_THRESHOLD = 0.3
FAISS_INDEX_PATH = "vector_store/ht.index"
ENTRIES_FILE_PATH = "vector_store/entries.json"
EMBEDDINGS_FILE_PATH = "vector_store/embeddings.npy"


def load_notes(filepath: str) -> List[str]:
    """Loads user notes from a JSON file."""
    try:
        with open(filepath) as f:
            return json.load(f)["notes"]
    except (FileNotFoundError, KeyError):
        return []


def find_and_generate_suggestions(
    entries: List[Tuple],
    embeddings: np.ndarray,
    indexer: FAISSHandler,
    sgllm: SuggestionGenerator,
    threshold: float,
    console: Console,
):
    """Searches the index with the given embeddings and generates suggestions."""
    if not entries:
        console.print("[yellow]No entries to search.[/yellow]")
        return

    console.print("\nSearching for connections...", style="bold green")
    similar_pairs = indexer.search(embeddings, top_k=5, threshold=threshold)

    if not similar_pairs:
        console.print("[yellow]No strong connections found between needs and available resources.[/yellow]")
        return

    for query_idx, result_idx, score in similar_pairs:
        type1 = entries[query_idx][1]
        type2 = entries[result_idx][1]

        if type1 == "need" and type2 == "availability":
            need_text = entries[query_idx][0]
            availability_text = entries[result_idx][0]

            with console.status("[bold green]Generating suggestion..."):
                suggestion_text = sgllm.generate(need_text, availability_text)

            suggestion_panel = Panel(
                f"[bold]Need:[/] [italic]{need_text}[/]\n"
                f"[bold]Availability:[/] [italic]{availability_text}[/]\n\n"
                f"---\n[bold bright_green]Suggestion:[/] {suggestion_text}",
                title="[bold yellow]💡 New Connection Found[/]",
                border_style="green",
                subtitle=f"Similarity: {score:.2f}",
            )
            console.print(suggestion_panel)


def main():
    """Main execution function."""
    load_dotenv()
    console = Console()

    API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        console.print("[bold red]Error:[/bold red] OPENROUTER_API_KEY not found in environment variables. Please create a .env file.")
        return

    # --- Initialization ---
    nat_filler = NATFiller(api_key=API_KEY)
    embedder = Embedder()
    indexer = FAISSHandler()
    sgllm = SuggestionGenerator(api_key=API_KEY)

    # --- Workflow ---
    # Check if pre-built index and data exist
    if all(os.path.exists(p) for p in [FAISS_INDEX_PATH, ENTRIES_FILE_PATH, EMBEDDINGS_FILE_PATH]):
        console.print(f"Loading pre-built index from [cyan]{FAISS_INDEX_PATH}[/cyan]...", style="bold green")
        indexer.load_index(FAISS_INDEX_PATH)

        console.print(f"Loading entries from [cyan]{ENTRIES_FILE_PATH}[/cyan]...", style="bold green")
        with open(ENTRIES_FILE_PATH) as f:
            entries = json.load(f)

        console.print(f"Loading embeddings from [cyan]{EMBEDDINGS_FILE_PATH}[/cyan]...", style="bold green")
        embeddings = np.load(EMBEDDINGS_FILE_PATH)

        if indexer.index.ntotal != len(embeddings):
            console.print("[bold red]Error:[/bold red] Index and embeddings are out of sync. Rebuilding index.")
        else:
            find_and_generate_suggestions(entries, embeddings, indexer, sgllm, SIMILARITY_THRESHOLD, console)
            return

    # If any file is missing or data is out of sync, rebuild everything
    console.print("\nBuilding index from scratch...", style="yellow")
    notes = load_notes(NOTES_FILEPATH)
    if not notes:
        console.print(f"[yellow]No notes found in {NOTES_FILEPATH}.[/yellow]")
        return

    nats = []
    for i, note_text in enumerate(notes):
        console.print(f"Processing Note {i + 1}...", style="cyan")
        nat_raw = nat_filler.fill_nat(note_text)
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```json\s*\n(.*?)\n```', nat_raw, re.DOTALL)
            if json_match:
                cleaned = json_match.group(1).strip()
            else:
                # Fallback: try to find JSON in the response
                json_match = re.search(r'\{.*\}', nat_raw, re.DOTALL)
                if json_match:
                    cleaned = json_match.group(0).strip()
                else:
                    # Last fallback: clean the old way
                    cleaned = re.sub(r"(^```json\s*|```$)", "", nat_raw.strip(), flags=re.MULTILINE)
            nat = json.loads(cleaned)
            nat.setdefault("resources_needed", [])
            nat.setdefault("resources_available", [])
            nat["original_note"] = note_text
            nat["id"] = i
            nats.append(nat)
        except (json.JSONDecodeError, TypeError):
            console.print(f"[bold red]Error:[/bold red] Could not parse JSON for Note {i+1}. Skipping.")

    entries = []
    for nat in nats:
        for need in nat.get("resources_needed", []):
            entries.append((need, "need", nat["id"]))
        for availability in nat.get("resources_available", []):
            entries.append((availability, "availability", nat["id"]))

    if not entries:
        console.print("[yellow]No entries found after processing. Nothing to embed or index.[/yellow]")
        return

    console.print("\nEmbedding notes and building index...", style="bold green")
    texts = [e[0] for e in entries]
    embeddings = np.array(embedder.get_embeddings(texts)).astype("float32")
    indexer.add(embeddings)

    # Save artifacts for next time
    console.print(f"Saving index to [cyan]{FAISS_INDEX_PATH}[/cyan]...", style="bold green")
    indexer.save_index(FAISS_INDEX_PATH)
    with open(ENTRIES_FILE_PATH, 'w') as f:
        json.dump(entries, f)
    np.save(EMBEDDINGS_FILE_PATH, embeddings)

    find_and_generate_suggestions(entries, embeddings, indexer, sgllm, SIMILARITY_THRESHOLD, console)


if __name__ == "__main__":
    main()