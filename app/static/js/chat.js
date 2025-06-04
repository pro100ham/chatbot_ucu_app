document.getElementById("send-button").addEventListener("click", sendMessage);

document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    chatBox.appendChild(botMessage);

    const model = getSelectedModel();
    const eventSource = new EventSource(`/intro?model=${model}`);
    window.currentEventSource = eventSource;

    let fullText = "";
    botMessage.classList.add("typing");

    eventSource.onmessage = function (event) {
        if (event.data) {
            if (event.data.includes("[SHOW_CRM_FORM]")) {
                fullText += event.data.replace("[SHOW_CRM_FORM]", "");
                botMessage.innerHTML = fullText.replace(/\n/g, "<br>");
                chatBox.scrollTop = chatBox.scrollHeight;
                renderCRMForm(fullText);
            } else {
                fullText += event.data;
                botMessage.innerHTML = fullText.replace(/\n/g, "<br>");
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }
    };

    eventSource.onerror = function () {
        botMessage.classList.remove("typing");
        eventSource.close();
    };
});

document.getElementById("model-selector").addEventListener("change", () => {
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";

    if (window.currentEventSource) {
        window.currentEventSource.close();
    }

    const model = getSelectedModel();
    const botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    chatBox.appendChild(botMessage);

    const eventSource = new EventSource(`/intro?model=${model}`);
    window.currentEventSource = eventSource;

    let fullText = "";
    botMessage.classList.add("typing");

    eventSource.onmessage = function (event) {
        if (event.data) {
            fullText += event.data;
            botMessage.innerHTML = fullText.replace(/\n/g, "<br>");
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    };

    eventSource.onerror = function () {
        botMessage.classList.remove("typing");
        eventSource.close();
    };
});

document.getElementById("user-input").addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

function getSelectedModel() {
    const selector = document.getElementById("model-selector");
    return selector ? selector.value : "ollama";
}

function sendMessage() {
    if (window.currentEventSource) {
        window.currentEventSource.close();
    }

    const model = getSelectedModel();
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    const chatBox = document.getElementById("chat-box");

    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    document.getElementById("user-input").value = "";

    const botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    chatBox.appendChild(botMessage);

    const eventSource = new EventSource(`/ask-stream?question=${encodeURIComponent(userInput)}&model=${model}`);
    window.currentEventSource = eventSource;

    eventSource.addEventListener("end", function () {
        eventSource.close();
    });

    let fullText = "";
    botMessage.classList.add("typing");
    let formRendered = false;

    eventSource.onmessage = function (event) {
        if (!event.data) return;

        fullText += event.data;
        botMessage.innerHTML = fullText.replace(/\n/g, "<br>");
        chatBox.scrollTop = chatBox.scrollHeight;

        if (!formRendered && fullText.includes("▶ Створити тікет")) {
            formRendered = true;
            renderCRMForm(fullText);
        }
    };

    eventSource.onopen = () => {
        console.log("✅ EventSource connection opened");
    };

    eventSource.onerror = (error) => {
        console.error("❌ EventSource error", error);
        botMessage.classList.remove("typing");
        eventSource.close();
    };
}

function renderCRMForm(question) {
    const formContainer = document.createElement("div");
    formContainer.className = "crm-form";

    formContainer.innerHTML = `
        <p><strong>Форма для створення тікету:</strong></p>
        <form id="crm-ticket-form">
            <input type="hidden" name="question" value="${question}">
            <input type="text" name="name" placeholder="Ваше ім’я" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="text" name="subject" placeholder="Тема звернення" required><br>
            <input type="tel" name="phone" placeholder="Номер телефону (необов’язково)"><br>
            <textarea name="description" rows="4" placeholder="Короткий опис проблеми..." required></textarea><br>
            <div style="text-align: right; margin-top: 10px;">
                <button type="submit">📨 Відправити запит</button>
            </div>
        </form>
    `;

    const chatBox = document.getElementById("chat-box");
    const lastBotMessage = chatBox.querySelector(".bot-message:last-of-type");
    if (lastBotMessage) {
        lastBotMessage.insertAdjacentElement("afterend", formContainer);
    } else {
        chatBox.appendChild(formContainer);
    }

    chatBox.scrollTop = chatBox.scrollHeight;

    const crmForm = document.getElementById("crm-ticket-form");
    crmForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(crmForm);
        const res = await fetch("/submit_crm_ticket", {
            method: "POST",
            body: formData
        });

        const result = await res.json();
        const msg = document.createElement("div");
        msg.className = "bot-message";
        msg.textContent = result.status === "success"
            ? "✅ Ваш запит було успішно надіслано!"
            : "❌ Сталася помилка при надсиланні запиту.";
        chatBox.appendChild(msg);

        formContainer.remove();
    });
}
