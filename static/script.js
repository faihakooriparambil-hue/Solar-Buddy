async function sendQuestion() {
    const input = document.getElementById("userInput").value;
    if (!input) return;

    const chat = document.getElementById("chat");
    chat.innerHTML += `<p><b>You:</b> ${input}</p>`;

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input })
    });

    const data = await response.json();
    chat.innerHTML += `<p><b>Solar Buddy:</b> ${data.answer}</p>`;
    document.getElementById("userInput").value = "";
    chat.scrollTop = chat.scrollHeight;
}
