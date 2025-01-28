const modal = document.getElementById("new--modal");
const btn = document.querySelector(".btn-new-message");
const btnStartChat = document.querySelector(".btn-start-chat");
const chatContainer = document.querySelector(".chat-container");
const closeBtn = document.querySelector(".close");
const friends = document.querySelectorAll(".friend-button");

btn.onclick = function () {
    modal.style.display = "flex";
    resetFriendDisplay();
}

if (btnStartChat) {
    btnStartChat.onclick = function () {
        modal.style.display = "flex";
        resetFriendDisplay();
    }
}

if (closeBtn) {
    closeBtn.onclick = function () {
        modal.style.display = "none";
    }
}

window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

function resetFriendDisplay() {
    for (let i = 0; i < friends.length; i++) {
        if (i < 5) {
            friends[i].style.display = "block";
        } else {
            friends[i].style.display = "none";
        }
    }
}

search = document.getElementById("search");

if (search) {
    search.addEventListener("input", function () {
        let friends = document.querySelectorAll(".friend-button");
        let searchValue = search.value.toLowerCase();
        if (searchValue) {
            for (let friend of friends) {
                if (friend.textContent.toLowerCase().includes(searchValue)) {
                    friend.style.display = "block";
                } else {
                    friend.style.display = "none";
                }
            }
        } else {
            resetFriendDisplay();
        }
    });
}
resetFriendDisplay();