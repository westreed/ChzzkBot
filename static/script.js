const ws = new WebSocket("ws://localhost:5005/ws");
const queue = [];

ws.onmessage = function(event) {
    const event_data = event.data;

    if (typeof event_data === "string") {
        const jsonData = JSON.parse(event_data);
        if (jsonData["event_type"] === "volume") {
            const audioPlayer = document.getElementById("player");
            audioPlayer.volume = jsonData["message"];
            console.log("Set TTS Volume ", jsonData["message"]);
        }
    } else {
        const audioBlob = new Blob([event_data], { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(audioBlob);
        queue.push(audioUrl);
    }
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