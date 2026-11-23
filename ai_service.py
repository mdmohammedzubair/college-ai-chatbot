import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")

def generate_answer(question, faqs):
    """
    Generate a grounded answer using a model running locally in Ollama.
    No paid API key or external AI service is used.
    """
    context = "\n\n".join(
        f"FAQ question: {item['question']}\nVerified answer: {item['answer']}"
        for item in faqs
    )

    system_prompt = (
    "You are a college FAQ assistant. "
    "Answer strictly using only the verified FAQ information provided. "
    "Never assume, guess, or infer missing college policies. "
    "Do not turn commonly requested documents into mandatory "
    "or optional requirements unless explicitly stated. "
    "If the FAQ does not directly answer any part of the question, "
    "clearly say that the information is not available and "
    "recommend contacting the college office. "
    "Be concise, friendly, and accurate."
)
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "stream": False,
                "think": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"VERIFIED COLLEGE FAQ INFORMATION:\n{context}\n\n"
                            f"STUDENT QUESTION:\n{question}"
                        )
                    }
                ],
                "options": {
                "temperature": 0.2,
                "num_ctx": 4096
              }
            },
            timeout=(5, 180)
        )
        response.raise_for_status()
        payload = response.json()
        answer = payload.get("message", {}).get("content", "").strip()
        if not answer:
            return "Sorry, I couldn't generate an answer. Please contact the college office."
        return answer
    except requests.exceptions.ConnectionError:
        return (
            "The local AI model is not running. Please start Ollama and make sure "
            f"the '{OLLAMA_MODEL}' model is installed, then try again."
        )
    except requests.exceptions.Timeout:
        return "The local AI is taking longer than expected. Please try a shorter question."
    except requests.exceptions.RequestException:
        return "Sorry, the local AI service is unavailable right now. Please try again later."
