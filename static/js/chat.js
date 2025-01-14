const conversationId = JSON.parse(document.getElementById('conversation').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + conversationId
    + '/'
);

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector('#chat-log');
    const newMessage = document.createElement('div');
    const username = data.username;
    const message = data.message;
    if (username !== undefined && message !== undefined) {
        newMessage.classList.add('chat-message');
        if (username === '{{ request.user.username }}') {
            newMessage.classList.add('my-message');
        }
        newMessage.innerHTML = `<strong class="username">${data.username}:</strong> <div class="message-container">${data.message} <span class="timestamp">(${new Date().toLocaleString()})</span></div>`;
        chatLog.appendChild(newMessage);
        chatLog.scrollTop = chatLog.scrollHeight;
    }
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.key === 'Enter') {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;

    chatSocket.send(JSON.stringify({
        'message': message,
        'username': '{{ request.user.username }}'
    }));
    messageInputDom.value = '';
};
