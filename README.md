# AI_Video_Assistant
# AI Meeting Assistant & Analyzer

This project is a comprehensive Python-based pipeline designed to automatically process, transcribe, and analyze meeting recordings or YouTube videos. It leverages local machine learning models and cloud APIs to generate summaries, extract key action items, and provide a Retrieval-Augmented Generation (RAG) interface for querying the meeting context.

## Core Features

* **Audio Ingestion & Processing:** Downloads media directly from YouTube URLs using `yt_dlp` or accepts local media files[cite: 17]. Uses `pydub` and `ffmpeg` to standardize the audio into 16kHz mono WAV format and splits it into manageable 10-minute chunks for processing[cite: 17].
* **Dual-Engine Transcription:** Supports local English transcription utilizing OpenAI's Whisper model[cite: 15]. Offers support for "Hinglish" audio by slicing the audio into 25-second pieces and passing them to the Sarvam AI API (`saaras:v2.5` model) for speech-to-text translation[cite: 15].
* **Intelligent Summarization:** Handles long meeting transcripts by chunking the text with `RecursiveCharacterTextSplitter` and processing it through a map-reduce pipeline using a Groq-hosted LLM (`openai/gpt-oss-20b`)[cite: 14]. Automatically generates a concise meeting title (maximum 8 words)[cite: 14].
* **Key Information Extraction:** Analyzes the transcript to identify and extract formatted action items, detailing the task, owner, and deadline[cite: 11]. Extracts a numbered list of key decisions made and any unresolved questions or follow-up topics[cite: 11].
* **Interactive Q&A (RAG):** Slices the transcript into 500-character chunks and embeds them into a persistent Chroma vector database using HuggingFace's `all-MiniLM-L6-v2` embeddings[cite: 16]. Enables users to ask direct questions about the meeting, answering based strictly on the retrieved context using a LangChain pipeline[cite: 13].
* **API Resilience:** Implements an automatic exponential backoff system to gracefully handle HTTP 429 rate-limit errors from the Groq API[cite: 12].

## System Architecture & Modules

* **`audio_preprocessing.py`**: Manages `yt_dlp` and `ffmpeg` interactions for downloading, formatting, and chunking audio inputs[cite: 17].
* **`transcriber.py`**: Routes chunks to either the local Whisper model or the external Sarvam API based on the selected language[cite: 15].
* **`summarizer.py`**: Executes the LangChain-based map-reduce summarization prompt chains and title generation[cite: 14].
* **`extractor.py`**: Contains the targeted prompt chains for pulling actionable items, decisions, and open questions[cite: 11].
* **`vectorstore.py`**: Manages the local Chroma vector database (`vector_db`) and HuggingFace embedding operations[cite: 16].
* **`rag_engine.py`**: Orchestrates the LangChain LCEL pipeline that retrieves context from Chroma and prompts the LLM for precise answers[cite: 13].
* **`llm.py`**: Provides the wrapper function (`invoke_with_rate_limit`) to ensure API call stability during high-volume inference[cite: 12].

## Prerequisites & Requirements

Before running the application, ensure you have the following system dependencies installed:

* **FFmpeg:** Must be installed and accessible on your system's PATH to enable audio extraction and conversion[cite: 17].

### Environment Variables

Configure the following environment variables to authenticate with the necessary services:

* `GROQ_API_KEY`: Required to use the `openai/gpt-oss-20b` model for summarization, extraction, and RAG operations[cite: 11, 13, 14].
* `SARVAM_API_KEY`: Required if utilizing the "Hinglish" transcription mode via Sarvam AI[cite: 15].
* `WHISPER_MODEL`: Optional. Defines the local Whisper model size to load (defaults to `"small"`)[cite: 15].
* `GROQ_MAX_RETRIES`: Optional. Defines the maximum number of retry attempts for 429 rate limit errors (defaults to `3`)[cite: 12].
