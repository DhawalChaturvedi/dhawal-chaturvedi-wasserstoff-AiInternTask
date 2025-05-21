# Document-based Chatbot with Thematic Synthesis

## Overview

This project implements a document-based chatbot system that allows users to:

- Upload multiple documents (PDFs, scanned images)
- Query individual documents for answers with citation references
- Fetch common themes across documents based on user queries
- Synthesize themes across all documents with summaries and citations
- Interact via a chat-style frontend interface

The backend is built with FastAPI exposing REST endpoints, while the frontend uses vanilla JavaScript to provide an interactive chat interface.

---

## Features

- **Document Upload:** Upload multiple files simultaneously with progress feedback.
- **Document Querying:** Ask questions targeting a specific document, receiving relevant extracted answers.
- **Theme Identification:** Discover common themes related to user queries across documents.
- **Cross-Document Synthesis:** Generate summarized themes with associated document citations.
- **Responsive Chat UI:** Messages appended dynamically with support for formatted HTML content.

---

## Installation

