const friendRequestSocket = new WebSocket(
    "wss://"
    + window.location.host
    + '/ws/friend_requests/'
);


friendRequestSocket.onclose = function (e) {
    console.error('Friend Requests socket closed unexpectedly');
};

const friendRequestBtn = document.getElementById('friend-request-btn');
const username = document.querySelector('.username-for-friend-requests')
if (friendRequestBtn && username) {
    friendRequestBtn.onclick = function () {

        friendRequestSocket.send(JSON.stringify({
            'message': 'Friend Request',
            'recipient': username.textContent,
            'sender': window.chatConfig.currentUserUsername
        }));
        console.log('Friend Request Sent');
    }
}