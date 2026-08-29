/* =========================
   TIME + DATE
========================= */

function updateDateTime() {

    const now = new Date();

    const time = now.toLocaleTimeString();

    const date = now.toLocaleDateString(
        undefined,
        {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        }
    );

    document.getElementById("time").textContent = time;

    document.getElementById("date").textContent = date;
}


updateDateTime();

setInterval(updateDateTime, 1000);


function speakText(text) {
    if (!('speechSynthesis' in window)) {
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
}


async function loadGreeting() {
    try {
        const result = await fetch('/api/greeting');
        const data = await result.json();
        document.getElementById('response').textContent = data.response;
        speakText(data.response);
    } catch (error) {
        document.getElementById('response').textContent = "Hello. I'm Milo.";
    }
}


loadGreeting();


/* =========================
   MILO EXPRESSIONS
========================= */

const expressions = [

    "assets/Milo_01_neutral.png",
    "assets/Milo_01_listening.png",
    "assets/Milo_01_thinking.png",
    "assets/Milo_01_happy.png"

];

let expressionIndex = 0;


const expressionButton = document.getElementById("expressionButton");

if (expressionButton) {
    expressionButton.addEventListener("click", function () {

        expressionIndex++;

        if (expressionIndex >= expressions.length) {
            expressionIndex = 0;
        }

        const milo = document.getElementById("milo");

        milo.style.opacity = "0";

        setTimeout(() => {

            milo.src = expressions[expressionIndex];

            milo.style.opacity = "1";

        }, 150);

    });
}


/* =========================
   MIC BUTTON
========================= */

let micOn = false;


document
    .getElementById("micButton")
    .addEventListener("click", function () {

        micOn = !micOn;

        const button = document.getElementById("micButton");

        const text = document.getElementById("micText");

        const waves = document.getElementById("waves");

        const milo = document.getElementById("milo");

        if (micOn) {

            button.classList.add("active");

            text.textContent = "MIC ON";

            waves.classList.add("active");

            milo.src = "assets/Milo_01_listening.png";

            document.getElementById("response").textContent =
                "I'm listening...";

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                document.getElementById("response").textContent =
                    "Voice input is not supported in this browser.";
                return;
            }

            const recognition = new SpeechRecognition();
            recognition.lang = "en-IN";
            recognition.interimResults = false;
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript;
                document.getElementById("response").textContent = query;
                milo.src = "assets/Milo_01_thinking.png";

                try {
                    const result = await fetch("/api/command", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ command: query })
                    });
                    const data = await result.json();
                    document.getElementById("response").textContent = data.response || data.error;
                    speakText(data.response || data.error);
                    milo.src = "assets/Milo_01_happy.png";
                } catch (error) {
                    document.getElementById("response").textContent =
                        "Milo could not reach the backend.";
                    milo.src = "assets/Milo_01_neutral.png";
                }
            };
            recognition.onerror = () => {
                document.getElementById("response").textContent = "I could not hear that command.";
            };
            recognition.onend = () => {
                button.classList.remove("active");
                text.textContent = "MIC OFF";
                waves.classList.remove("active");
                micOn = false;
            };
            recognition.start();

        } else {

            button.classList.remove("active");

            text.textContent = "MIC OFF";

            waves.classList.remove("active");

            milo.src = "assets/Milo_01_neutral.png";

            document.getElementById("response").textContent =
                "Microphone is off.";

        }

    });