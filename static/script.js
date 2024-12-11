const ws = new WebSocket("ws://localhost:5005/ws");
const queue = [];

ws.onmessage = function(event) {
    console.log(event);
    const audioBlob = new Blob([event.data], { type: 'audio/mp3' });
    const audioUrl = URL.createObjectURL(audioBlob);
    queue.push(audioUrl);
//    const audioPlayer = document.getElementById("audioPlayer");
//    audioPlayer.src = audioUrl;
//    audioPlayer.play();
};


async function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}


function play_tts(src) {
    return new Promise((resolve, reject) => {
        const audioPlayer = document.getElementById("player");
        audioPlayer.src = src;

        // 에러 발생 시 reject
        audioPlayer.onerror = () => reject(new Error("Failed to load audio"));

        // 재생이 끝나면 resolve
        audioPlayer.onended = () => resolve();

        // 오디오 재생
        audioPlayer.play().catch((err) => reject(err));
    });
}

async function main() {
    while (ws) {
        try {
            if (queue.length > 0) {
                audio = queue.shift();
                await play_tts(audio).catch((err) => console.log(err));
            }
        } catch (err) {
            console.log(err);
        }
        await sleep(100);
    }
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    ws.send(input.value);
    input.value = '';
}

main()