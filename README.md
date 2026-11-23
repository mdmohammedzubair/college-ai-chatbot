# AI-Powered College FAQ Chatbot — Free Local AI Edition

A Flask college website chatbot using:
- Python Flask backend
- SQLite FAQ and chat-history database
- Ollama to run a local open-weight language model
- Qwen3.5 4B as the default local model
- HTML, CSS and JavaScript frontend

**No paid API key is required.** The model runs on your own computer. An internet connection is needed initially to install Ollama and download the model; after that, chat generation can run locally.

## Recommended computer profile
This project is configured for a Windows 11 computer with 16 GB RAM. Since the exact Ryzen processor and GPU are not yet known, start with `qwen3.5:4b`, a smaller model that is a sensible first test for CPU or integrated-graphics use. Larger models may run, but can be slower or leave too little memory for Windows and VS Code.

## 1. Install Ollama on Windows 11
1. Download Ollama from https://ollama.com/download/windows
2. Run the installer.
3. Open PowerShell or the VS Code terminal.
4. Download the model:

```powershell
ollama pull qwen3.5:4b
```

5. Test it:

```powershell
ollama run qwen3.5:4b
```

Ask it a simple question. Type `/bye` to exit the interactive chat. Ollama should remain available in the background.

To check that the model is installed:

```powershell
ollama list
```

## 2. Set up the Flask project
Open this project folder in VS Code. In its terminal:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## 3. Configure the local AI connection
Copy `.env.example` and rename the copy to `.env`.

The default values are:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
```

No API key is needed. Do not add a paid API key.

## 4. Run the website
Make sure Ollama is running, then from the project folder:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The SQLite database and sample FAQ records are created automatically on first run.

## 5. Test the chatbot
Try:
- How can I apply for admission?
- What documents are required for admission?
- How do I pay my tuition fees?
- Does the college provide placement support?
- What is the admission deadline?

The bot should answer only from the FAQ information retrieved from SQLite. If it cannot find relevant FAQ entries, the application returns a safe fallback rather than asking the model to guess.

## 6. Customize the college data
Edit `SAMPLE_FAQS` in `database.py`. Replace the demo university name and sample FAQ answers with information verified by your college.

If you change the initial FAQ seed list and want a fresh database, stop Flask and delete `database/college.db`. The app recreates it on the next run. This deletes stored demo chat history too.

## 7. Troubleshooting
- **`ollama` is not recognized:** close and reopen the terminal after installing Ollama.
- **Connection refused / local AI not running:** open the Ollama app or run `ollama serve` in a separate terminal.
- **Model not found:** run `ollama pull qwen3.5:4b`.
- **Slow answers:** close memory-heavy apps and test short questions. CPU-only generation can be slower than GPU-assisted generation.
- **Need to see whether GPU is used:** run `ollama ps` after sending a chatbot question.

## Architecture
Browser → Flask `/api/chat` → SQLite FAQ retrieval → Ollama local `/api/chat` endpoint → Qwen3.5 4B → SQLite chat history → Browser.

## Academic and safety notes
This is an internship prototype, not an official student-information system. Replace all sample answers with approved college information. Do not store private student records, passwords, marks, medical information or other sensitive data in this demo.

Before real deployment, add admin authentication, rate limiting, CSRF protection, privacy/retention controls, production logging, robust semantic retrieval and a review process for FAQ changes.

Ollama is the local model runner; the selected language model has its own licence and usage terms. Check the model's official listing before redistributing or deploying it.
