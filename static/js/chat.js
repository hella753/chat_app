
const conversationId = JSON.parse(document.getElementById('conversation').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + conversationId
    + '/'
); // WebSocket connection


chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector('#chat-log');
    const newMessage = document.createElement('div');
    const username = data.username;
    const message = data.message;

    console.log(data);

    let fileContent = '';
    const file = data.file;
    if (file) {
        const mimeType = file.split(';')[0].split(':')[1];
        if (mimeType.startsWith('image/')) {
            fileContent = `<img src="${file}" alt="file" class="message-file">`;
        } else {
            fileContent = `<a href="${file}" download class="message-file">🔗 Download</a>`;
        }
    } // Handle file content

    if (username !== undefined && message !== undefined) {
        newMessage.classList.add('chat-message');
        const user = window.chatConfig.currentUserUsername
        if (username === user) {
            newMessage.classList.add('my-message');
        }
        newMessage.innerHTML = `
        <strong class="username">${data.username}:</strong> 
        <div class="message-container">
            ${data.message}
            ${fileContent}
            <span class="timestamp">
                (${new Date().toLocaleString()})
            </span>
        </div>`;
        chatLog.appendChild(newMessage);
        chatLog.scrollTop = chatLog.scrollHeight;
    } // Handle message content

    if (data.type === 'online_users') {
        const onlineUsers = data.online_users;
        const chatName = data.chat_name;
        const circles = document.querySelectorAll('[id^="circle_"]');

        circles.forEach(circle => {
            if (circle.id.includes('QuerySet')) { // For group chats
                const excludedCurrentUsername = onlineUsers.filter(
                    username => username !== window.chatConfig.currentUserUsername
                );
                if (excludedCurrentUsername.length > 0) {
                    circle.classList.remove('circle-inactive');
                    circle.classList.add('circle-active');
                } else {
                    circle.classList.remove('circle-active');
                    circle.classList.add('circle-inactive');
                }

            } else {
                const username = circle.id.replace('circle_', '');
                if (onlineUsers.includes(username)) {
                    circle.classList.remove('circle-inactive');
                    circle.classList.add('circle-active');
                } else {
                    circle.classList.remove('circle-active');
                    circle.classList.add('circle-inactive');
                }
            }
        });
    } // Handle online users
};


chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
}; // WebSocket close event

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.key === 'Enter') {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
}; // Submit a message on enter key press

const fileStatusDom = document.querySelector('#file-upload-status');
const fileInputDom = document.querySelector('#file-upload');

fileInputDom.addEventListener('change', () => {
    if (fileInputDom.files.length > 0) {
        fileStatusDom.style.background = '#86A788'
    } else {
        fileStatusDom.style.background = 'none';
    }
}); // Change file status color

document.querySelector('#chat-message-submit').onclick = async function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    const fileInputDom = document.querySelector('#file-upload');
    const file = fileInputDom.files[0];

    let fileData = null;
    if (file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        fileData = await new Promise(resolve => {
            reader.onload = () => resolve(reader.result);
        });
    }
    chatSocket.send(JSON.stringify({
        'message': message,
        'file': fileData ? fileData : null,
        'username': window.chatConfig.currentUserUsername,
    }));

    messageInputDom.value = '';
    fileInputDom.value = '';
    fileStatusDom.style.background = 'none';
}; // Send a message on submitting

window.onload = function () {
    const chatLog = document.querySelector('#chat-log');
    chatLog.scrollTop = chatLog.scrollHeight;
}; // Scroll to the bottom of the chat log on a page load

