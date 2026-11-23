
const launcher = document.getElementById("chatLauncher");
const panel = document.getElementById("chatPanel");
const closeBtn = document.getElementById("closeChat");
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const body = document.getElementById("chatBody");

launcher.addEventListener("click", () => {
  panel.hidden = false;
  launcher.hidden = true;
  input.focus();
});

closeBtn.addEventListener("click", () => {
  panel.hidden = true;
  launcher.hidden = false;
});

// Safely display bold Markdown without allowing HTML injection.
function renderMessageText(element, text) {
  const parts = String(text).split(/(\*\*[\s\S]+?\*\*)/g);

  parts.forEach(part => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      const strong = document.createElement("strong");
      strong.textContent = part.slice(2, -2);
      element.appendChild(strong);
    } else {
      element.appendChild(document.createTextNode(part));
    }
  });
}

function addMessage(text, role) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const p = document.createElement("p");

  if (role === "bot") {
    renderMessageText(p, text);
  } else {
    p.textContent = text;
  }

  wrapper.appendChild(p);
  body.appendChild(wrapper);
  body.scrollTop = body.scrollHeight;

  return wrapper;
}

async function sendMessage(text) {
  addMessage(text, "user");

  const loading = addMessage("Thinking...", "bot");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: text })
    });

    const data = await response.json();

    loading.remove();

    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    addMessage(data.answer, "bot");

  } catch (error) {
    loading.remove();
    addMessage(
      error.message || "Unable to connect. Please try again.",
      "bot"
    );
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = input.value.trim();

  if (!text) return;

  input.value = "";
  await sendMessage(text);
});

document.querySelectorAll(".suggestions button").forEach(button => {
  button.addEventListener("click", () => {
    sendMessage(button.textContent.trim());
  });
});
