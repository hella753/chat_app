const notificationSocket = new WebSocket(
    "wss://"
    + window.location.host
    + '/ws/notifications/'
);

notificationSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const sender = data['sender'];

    const message = data['message'];
    const notificationContainer = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.classList.add('notification');
    notification.innerHTML = `
        <strong>${sender}</strong>: ${message}
        <button class="close-btn" onclick="closeNotification(this)">x</button>
    `;

    notificationContainer.appendChild(notification);

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        notification.remove();
        }, 5000);
};

function closeNotification(button) {
    button.parentElement.remove();
}
