import math
import re
from pathlib import Path

from pypdf import PdfReader


PDF_DIRECTORY = Path(__file__).resolve().parent / "faa_maintenance_pdfs"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i",
    "in", "is", "it", "me", "of", "on", "or", "the", "to", "what",
    "when", "who", "with", "faa", "federal", "aviation", "administration",
    "cfr", "part", "14", "aircraft", "maintenance", "may", "perform",
    "performing", "performed", "as", "current", "latest", "requirements",
    "requirement", "2026",
}
FAA_QUERY_TERMS = (
    "faa",
    "federal aviation administration",
    "14 cfr",
    "maintenance",
    "aircraft maintenance",
    "preventive maintenance",
    "maintenance record",
    "maintenance records",
    "maintenance log",
    "aircraft logbook",
    "aircraft inspection",
    "annual inspection",
    "100-hour inspection",
    "100 hour inspection",
    "aircraft repair",
    "aircraft mechanic",
    "airworthiness",
    "return to service",
    "airworthiness directive",
    "part 43",
    "14 cfr 43",
)
MIN_MATCHED_TERM_RATIO = 0.4


def is_faa_query(query: str) -> bool:
    normalized_query = query.casefold()
    return any(term in normalized_query for term in FAA_QUERY_TERMS)


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.casefold())
        if token not in STOP_WORDS
    ]


def _load_pdf_pages() -> list[dict[str, str | int | list[str]]]:
    pages = []
    for pdf_path in sorted(PDF_DIRECTORY.glob("*.pdf")):
        for page_number, page in enumerate(PdfReader(str(pdf_path)).pages, start=1):
            content = " ".join((page.extract_text() or "").split())
            tokens = _tokenize(content)
            if tokens:
                pages.append(
                    {
                        "source": pdf_path.name,
                        "page": page_number,
                        "content": content,
                        "tokens": tokens,
                    }
                )
    return pages


def retrieve_maintenance_context(query: str, top_k: int = 3) -> list[dict[str, str | int]]:
    pages = _load_pdf_pages()
    query_terms = set(_tokenize(query))
    if not pages or not query_terms:
        return []

    average_length = sum(len(page["tokens"]) for page in pages) / len(pages)
    document_frequencies = {
        term: sum(term in set(page["tokens"]) for page in pages)
        for term in query_terms
    }
    ranked_pages = []

    for page in pages:
        tokens = page["tokens"]
        term_frequencies = {term: tokens.count(term) for term in query_terms}
        matched_term_ratio = sum(
            frequency > 0 for frequency in term_frequencies.values()
        ) / len(query_terms)
        score = 0.0
        for term, frequency in term_frequencies.items():
            if not frequency:
                continue
            document_frequency = document_frequencies[term]
            inverse_document_frequency = math.log(
                1 + (len(pages) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            length_normalization = frequency + 1.5 * (
                1 - 0.75 + 0.75 * len(tokens) / average_length
            )
            score += inverse_document_frequency * frequency * 2.5 / length_normalization
        if score > 0 and matched_term_ratio >= MIN_MATCHED_TERM_RATIO:
            ranked_pages.append((score, page))

    ranked_pages.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "source": page["source"],
            "page": page["page"],
            "content": page["content"],
        }
        for _, page in ranked_pages[:top_k]
    ]