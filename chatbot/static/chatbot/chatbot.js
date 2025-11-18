// function toggleChat() {
//     const chat = document.getElementById("chat-container");
//     chat.style.display = chat.style.display === "none" ? "flex" : "none";
// }

// function sendMessage() {
//     const userInput = document.getElementById("user-input");
//     const message = userInput.value.trim();
//     if (!message) return;

//     const chatBox = document.getElementById("chat-box");
//     chatBox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;

//     fetch(`/chatbot/get_response/?msg=${encodeURIComponent(message)}`)
//         .then(response => response.json())
//         .then(data => {
//             chatBox.innerHTML += `<div><strong>Bot:</strong> ${data.reply}</div>`;
//             chatBox.scrollTop = chatBox.scrollHeight;
//         })
//         .catch(error => {
//             chatBox.innerHTML += `<div><strong>Bot:</strong> Oops! Error getting response.</div>`;
//             console.error('Error:', error);
//         });

//     userInput.value = "";
// }

let hasOpenedBefore = false;

function toggleChat() {
    const chat = document.getElementById("chat-container");
    const chatBox = document.getElementById("chat-box");

    if (chat.style.display === "none") {
        chat.style.display = "flex";
        if (!hasOpenedBefore) {
            chatBox.innerHTML += `<div><strong>Suraksha Bot:</strong> Hi! How can I assist you with crime data analysis?</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            hasOpenedBefore = true;
        }
    } else {
        chat.style.display = "none";
    }
}

function sendMessage() {
    const userInput = document.getElementById("user-input");
    const message = userInput.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;

    fetch(`/chatbot/get_response/?msg=${encodeURIComponent(message)}`)
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += `<div><strong>Suraksha Bot:</strong> ${data.reply}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            chatBox.innerHTML += `<div><strong>Suraksha Bot:</strong> Oops! Error getting response.</div>`;
            console.error('Error:', error);
        });

    userInput.value = "";
}

function quickMessage(message) {
    const userInput = document.getElementById("user-input");
    userInput.value = message;
    sendMessage();
}
