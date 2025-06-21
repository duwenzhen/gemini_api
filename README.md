# Gemini Email Assistant: AI-Powered Email Summaries and Voice Memos
A proof-of-concept project that uses a chain of Gemini API calls, orchestrated with the Gmail API, to automatically fetch, analyze, summarize, and convert your emails into voice notes delivered straight to your inbox.

## Purpose

**While this project currently serves an educational purpose, it's fundamentally a proof-of-concept for a feature I foresee becoming standard. The potential for an intelligent email assistant is universal, and it's only a matter of time before such capabilities are built natively into platforms like Gmail. This exploration is fueled by curiosity and the ethos:**

> "Stay hungry, stay foolish."

## Overview
In an era of information overload, managing an email inbox can be a significant challenge. This project explores a solution by leveraging the power of Large Language Models (LLMs) to create a personal email assistant.

The core idea is simple: prompt the assistant to summarize your emails from a specific period. In the background, a multi-step process is initiated: emails are fetched, intelligently filtered to remove noise, summarized into a concise brief, converted into an audio file, and delivered back to you.

The primary goal of this project is educational—to gain hands-on experience with:

* Google's Gemini API: Exploring its capabilities for function calling and text generation.
* Gmail API: Programmatically accessing and managing email data.
* Multi-Step Agent Orchestration: Chaining multiple AI and tool calls together to perform a complex task.
This project serves as a practical exploration of what the future of native email clients could look like.

## How It Works
The workflow is orchestrated through a sequence of API calls, where the output of one step serves as the input for the next.

### 1. Email Fetching (Tool Call #1):

* A user provides a natural language prompt (e.g., "Please summarize the emails I received yesterday").
* The first Gemini model interprets the prompt and uses the Gmail API tool to fetch all relevant emails within the specified date range.

### 2. Content Analysis & Summarization (Model Call #2):

* The raw email data is passed to a second Gemini model.
* This model is prompted to perform a specific analysis:
  * Filter out promotional, marketing, and non-essential content.
    * Focus exclusively on personal and important correspondence.
    * Generate a concise, easy-to-read summary of the key information from the filtered emails.

### 3. Text-to-Speech Conversion (Model Call #3):

* The generated text summary is then sent to a third service.
* This service converts the text summary into a high-quality audio file (e.g., MP3 or WAV).

### 4. Delivery to Inbox:

* Finally, the system uses the Gmail API again to compose and send a new email to your own address.
* Subject: "Your Email Summary"
* Body: The text summary.
* Attachment: The generated audio summary.

## Tech Stack
* Language: Python
* Dependency Management: Poetry
* Core APIs:
  * Google Gemini API
  * Google Gmail API
  * Google Gemini Text-to-Speech Model (or other TTS service)
* Key Libraries:
  * google-generativeai
  * google-api-python-client
  * google-auth-oauthlib

## Future Work
This is an initial version built for learning and demonstration. Future enhancements could include:

* Developing a simple web interface (e.g., using Flask or Streamlit).
* Adding support for more complex queries and filters.
* Packaging the application into a container for easier deployment.
* Writing a detailed Medium article about the development process and learnings.