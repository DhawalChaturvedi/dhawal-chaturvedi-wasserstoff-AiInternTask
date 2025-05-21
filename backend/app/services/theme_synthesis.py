from app.services.grok_api import grok_chat_completion

# Template prompt for Grok model to summarize themes and cite documents
THEME_PROMPT_TEMPLATE = """
You are an AI research assistant. Analyze the following excerpts grouped by theme. Summarize each theme clearly and list the cited documents (by doc ID or filename and page).

Text Group:
{group_text}

Format:
Theme Title: <summary>
Cited Documents: <doc_id or filename + page>
"""

# Prompt for precise extracted answer per document
EXTRACT_PROMPT_TEMPLATE = """
You are a legal assistant. From the following document excerpts, extract one concise sentence that best supports the main theme discussed above.

Only provide:
Extracted Answer: <one specific sentence>
Citation: Page X, Para Y

Excerpts:
{doc_chunks}
"""

def identify_themes(chunks: list, theme_id: int):
    """
    Function:
    Uses Groq API to summarize grouped theme chunks and generate one clear supporting sentence per document.

    Returns:
    - summary: Full theme summary
    - citations: Unique doc_ids
    - answers: List of extracted sentence + citation per document
    """
    # 1. Generate joined text for the theme summary
    joined_text = ""
    for chunk in chunks:
        filename = chunk.get('filename', 'Unknown')
        page = chunk.get('page', '?')
        text = chunk.get('text', '')
        joined_text += f"[{filename} p.{page}]: {text}\n\n"

    # 2. Call Groq for the theme summary
    prompt = THEME_PROMPT_TEMPLATE.format(group_text=joined_text)
    summary = grok_chat_completion(prompt, max_tokens=900)

    # 3. Group chunks by doc_id to extract one focused answer per document
    grouped_by_doc = {}
    for chunk in chunks:
        doc_id = chunk.get("doc_id", "Unknown")
        grouped_by_doc.setdefault(doc_id, []).append(chunk)

    answers = []
    for doc_id, doc_chunks in grouped_by_doc.items():
        combined = "\n".join(f"[Page {c.get('page', '?')}, Para {c.get('paragraph', '?')}]: {c.get('text', '')}" for c in doc_chunks)
        extract_prompt = EXTRACT_PROMPT_TEMPLATE.format(doc_chunks=combined)

        try:
            result = grok_chat_completion(extract_prompt, max_tokens=250)
            split_parts = result.strip().split("Citation:")
            answer_text = split_parts[0].replace("Extracted Answer:", "").strip()
            citation = split_parts[1].strip() if len(split_parts) > 1 else "Unknown"
        except Exception as e:
            answer_text = "Error generating answer."
            citation = "N/A"

        answers.append({
            "doc_id": doc_id,
            "text": answer_text,
            "citation": citation
        })

    return {
        "summary": summary.strip(),
        "citations": list(grouped_by_doc.keys()),
        "answers": answers
    }
