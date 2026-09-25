// ======================================================
// ELEMENTOS PRINCIPAIS
// ======================================================

const messageForm =
    document.getElementById("messageForm");

const messageInput =
    document.getElementById("messageInput");

const messages =
    document.getElementById("messages");

const sendButton =
    document.getElementById("sendButton");

const newChat =
    document.getElementById("newChat");

const suggestions =
    document.querySelectorAll(".suggestion");

const voiceButton =
    document.getElementById("voiceButton");


// ======================================================
// ESTADO
// ======================================================

let isGenerating = false;
let thinkingMessage = null;


// ======================================================
// UTILIDADES
// ======================================================

function getCurrentTime() {
    return new Date().toLocaleTimeString(
        "pt-BR",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


function removeWelcome() {
    const welcome =
        document.querySelector(".welcome");

    const terminalWelcome =
        document.querySelector(
            ".welcome-terminal"
        );

    if (welcome) {
        welcome.remove();
    }

    if (terminalWelcome) {
        terminalWelcome.remove();
    }
}


function scrollToBottom() {
    messages.scrollTo({
        top: messages.scrollHeight,
        behavior: "smooth"
    });
}


function resizeTextarea() {
    messageInput.style.height =
        "auto";

    messageInput.style.height =
        `${messageInput.scrollHeight}px`;
}


// ======================================================
// ESCAPE HTML
// ======================================================

function escapeHTML(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ======================================================
// SYSTEM MONITOR
// ======================================================

function createAsciiBar(
    percentage,
    size = 12
) {
    if (
        percentage === null ||
        percentage === undefined
    ) {
        return `[${"?".repeat(size)}]`;
    }

    const value = Math.max(
        0,
        Math.min(
            100,
            Number(percentage)
        )
    );

    const filled = Math.round(
        (value / 100) * size
    );

    const empty =
        size - filled;

    return (
        "[" +
        "█".repeat(filled) +
        "·".repeat(empty) +
        "]"
    );
}


function getLoadState(value) {
    const usage = Number(value);

    if (Number.isNaN(usage)) {
        return "UNKNOWN";
    }

    if (usage >= 90) {
        return "CRITICAL";
    }

    if (usage >= 70) {
        return "HIGH";
    }

    if (usage >= 40) {
        return "ACTIVE";
    }

    return "NORMAL";
}


async function updateSystemMonitor() {
    try {
        const response = await fetch(
            "/api/system",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                "SYSTEM MONITOR OFFLINE"
            );
        }

        const data =
            await response.json();


        // ==========================================
        // CPU
        // ==========================================

        const cpuValue =
            document.getElementById(
                "cpuValue"
            );

        const cpuBar =
            document.getElementById(
                "cpuBar"
            );

        const cpuInfo =
            document.getElementById(
                "cpuInfo"
            );

        if (cpuValue) {
            cpuValue.textContent =
                `${data.cpu.usage}%`;
        }

        if (cpuBar) {
            cpuBar.textContent =
                createAsciiBar(
                    data.cpu.usage
                );

            cpuBar.dataset.state =
                getLoadState(
                    data.cpu.usage
                );
        }

        if (cpuInfo) {
            let info =
                `${data.cpu.cores_physical}C / ` +
                `${data.cpu.cores_logical}T`;

            if (data.cpu.frequency) {
                info +=
                    ` // ${Math.round(
                        data.cpu.frequency
                    )} MHz`;
            }

            cpuInfo.textContent =
                info;
        }


        // ==========================================
        // GPU
        // ==========================================

        const gpuValue =
            document.getElementById(
                "gpuValue"
            );

        const gpuBar =
            document.getElementById(
                "gpuBar"
            );

        const gpuInfo =
            document.getElementById(
                "gpuInfo"
            );

        if (gpuValue) {
            gpuValue.textContent =
                data.gpu.usage !== null &&
                data.gpu.usage !== undefined
                    ? `${data.gpu.usage}%`
                    : "N/A";
        }

        if (gpuBar) {
            gpuBar.textContent =
                createAsciiBar(
                    data.gpu.usage
                );

            gpuBar.dataset.state =
                getLoadState(
                    data.gpu.usage
                );
        }

        if (gpuInfo) {
            gpuInfo.textContent =
                data.gpu.name ||
                "GPU UNKNOWN";
        }


        // ==========================================
        // RAM
        // ==========================================

        const ramValue =
            document.getElementById(
                "ramValue"
            );

        const ramBar =
            document.getElementById(
                "ramBar"
            );

        const ramInfo =
            document.getElementById(
                "ramInfo"
            );

        if (ramValue) {
            ramValue.textContent =
                `${data.memory.usage}%`;
        }

        if (ramBar) {
            ramBar.textContent =
                createAsciiBar(
                    data.memory.usage
                );

            ramBar.dataset.state =
                getLoadState(
                    data.memory.usage
                );
        }

        if (ramInfo) {
            ramInfo.textContent =
                `${data.memory.used_gb} GB / ` +
                `${data.memory.total_gb} GB`;
        }


        // ==========================================
        // DISCOS
        // ==========================================

        const diskMonitor =
            document.getElementById(
                "diskMonitor"
            );

        if (diskMonitor) {
            diskMonitor.innerHTML = "";

            data.disks.forEach(
                disk => {

                    const item =
                        document.createElement(
                            "div"
                        );

                    item.classList.add(
                        "system-metric",
                        "disk-item"
                    );

                    const state =
                        getLoadState(
                            disk.usage
                        );

                    item.innerHTML = `
                        <div
                            class="system-metric-header"
                        >

                            <span>
                                DISK ${escapeHTML(
                                    disk.device
                                )}
                            </span>

                            <span>
                                ${disk.usage}%
                            </span>

                        </div>


                        <div
                            class="ascii-progress"
                            data-state="${state}"
                        >
                            ${createAsciiBar(
                                disk.usage
                            )}
                        </div>


                        <div
                            class="system-metric-info"
                        >
                            ${disk.used_gb} GB /
                            ${disk.total_gb} GB
                            //
                            FREE ${disk.free_gb} GB
                        </div>
                    `;

                    diskMonitor.appendChild(
                        item
                    );
                }
            );
        }


        // ==========================================
        // UPTIME
        // ==========================================

        const uptimeValue =
            document.getElementById(
                "uptimeValue"
            );

        if (uptimeValue) {
            uptimeValue.textContent =
                data.uptime.formatted;
        }


        // ==========================================
        // LIVE STATUS
        // ==========================================

        const liveStatus =
            document.getElementById(
                "systemLiveStatus"
            );

        if (liveStatus) {
            liveStatus.textContent =
                "LIVE";

            liveStatus.dataset.state =
                "online";
        }

    }

    catch (error) {
        console.error(
            "[SYSTEM MONITOR]",
            error
        );


        const liveStatus =
            document.getElementById(
                "systemLiveStatus"
            );

        if (liveStatus) {
            liveStatus.textContent =
                "OFFLINE";

            liveStatus.dataset.state =
                "offline";
        }
    }
}


// ======================================================
// FORMATAÇÃO DO CLIMA
// ======================================================

function formatWeatherTime(value) {
    if (!value) {
        return "--:--";
    }

    if (value.includes("T")) {
        return value.split("T")[1];
    }

    return value;
}


function formatWeatherDate(value) {
    if (!value) {
        return "--/--/----";
    }

    const parts =
        value.split("-");

    if (parts.length !== 3) {
        return value;
    }

    const [
        year,
        month,
        day
    ] = parts;

    return `${day}/${month}/${year}`;
}


// ======================================================
// ASCII CLIMA
// ======================================================

function getWeatherASCII(
    rainChance = 0,
    precipitation = 0
) {
    if (
        Number(rainChance) >= 60 ||
        Number(precipitation) >= 5
    ) {
        return `
           .--.
        .-(    ).
       (___.__)__)
        / / / /
       / / / /
      / / / /
     SIGNAL: RAIN
        `.trim();
    }


    if (
        Number(rainChance) >= 20 ||
        Number(precipitation) > 0
    ) {
        return `
          \\   /
           .-.
       ―  (   )  ―
           \`-'
          /   \\
              .--.
           .-(    ).
          (___.__)__)
     SIGNAL: CLOUD
        `.trim();
    }


    return `
          \\   /
           .-.
       ―  (   )  ―
           \`-'
          /   \\

       SIGNAL: CLEAR
    `.trim();
}


// ======================================================
// MENSAGEM NORMAL
// ======================================================

function addMessage(
    author,
    content,
    responseTime = null
) {
    removeWelcome();


    const message =
        document.createElement(
            "div"
        );

    message.classList.add(
        "message",
        author
    );


    if (author === "celene") {
        const avatar =
            document.createElement(
                "div"
            );

        avatar.classList.add(
            "message-avatar"
        );

        avatar.textContent =
            "C";

        message.appendChild(
            avatar
        );
    }


    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.classList.add(
        "message-wrapper"
    );


    const messageContent =
        document.createElement(
            "div"
        );

    messageContent.classList.add(
        "message-content"
    );

    messageContent.textContent =
        content;

    wrapper.appendChild(
        messageContent
    );


    const meta =
        document.createElement(
            "div"
        );

    meta.classList.add(
        "message-meta"
    );


    const time =
        document.createElement(
            "span"
        );

    time.textContent =
        getCurrentTime();

    meta.appendChild(
        time
    );


    if (
        author === "celene" &&
        responseTime !== null &&
        responseTime !== undefined
    ) {
        const performance =
            document.createElement(
                "span"
            );

        performance.classList.add(
            "message-performance"
        );

        performance.textContent =
            `// ${responseTime}s`;

        meta.appendChild(
            performance
        );
    }


    wrapper.appendChild(meta);
    message.appendChild(wrapper);
    messages.appendChild(message);


    requestAnimationFrame(
        () => {
            message.classList.add(
                "message-visible"
            );
        }
    );


    scrollToBottom();
}


// ======================================================
// THINKING
// ======================================================

function showThinking() {
    removeWelcome();


    if (thinkingMessage) {
        return;
    }


    thinkingMessage =
        document.createElement(
            "div"
        );

    thinkingMessage.classList.add(
        "message",
        "celene",
        "thinking-message"
    );


    const avatar =
        document.createElement(
            "div"
        );

    avatar.classList.add(
        "message-avatar"
    );

    avatar.textContent = "C";


    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.classList.add(
        "thinking-wrapper"
    );


    wrapper.innerHTML = `
        <span>
            CELENE&gt; PROCESSING
        </span>

        <div class="thinking-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;


    thinkingMessage.appendChild(
        avatar
    );

    thinkingMessage.appendChild(
        wrapper
    );

    messages.appendChild(
        thinkingMessage
    );


    requestAnimationFrame(
        () => {
            thinkingMessage.classList.add(
                "message-visible"
            );
        }
    );


    scrollToBottom();
}


function removeThinking() {
    if (!thinkingMessage) {
        return;
    }

    thinkingMessage.remove();

    thinkingMessage = null;
}


// ======================================================
// ESTADO DE GERAÇÃO
// ======================================================

function setGenerating(state) {
    isGenerating = state;


    if (state) {
        messageInput.disabled = true;

        sendButton.classList.add(
            "generating"
        );

        sendButton.textContent =
            "WAIT";

        return;
    }


    messageInput.disabled = false;

    sendButton.classList.remove(
        "generating"
    );

    sendButton.textContent =
        "EXEC";

    messageInput.focus();
}


// ======================================================
// WEATHER ASCII
// ======================================================

function addWeatherMessage(result) {
    removeWelcome();


    const data =
        result.data;


    if (!data) {
        addMessage(
            "celene",
            result.response,
            result.response_time
        );

        return;
    }


    const message =
        document.createElement(
            "div"
        );

    message.classList.add(
        "message",
        "celene",
        "weather-message"
    );


    const wrapper =
        document.createElement(
            "section"
        );

    wrapper.classList.add(
        "ascii-weather"
    );


    const ascii =
        getWeatherASCII(
            data.rain,
            data.precipitation
        );


    wrapper.innerHTML = `
        <div class="ascii-weather-header">

            <div class="ascii-weather-title">

                <span class="ascii-box">
                    C
                </span>

                <div>

                    <strong>
                        PREVISÃO DO TEMPO
                    </strong>

                    <small>
                        SYS://WEATHER_MODULE
                    </small>

                </div>

            </div>


            <div class="ascii-weather-location">

                <span>
                    LOCAL:
                </span>

                <strong>
                    ${escapeHTML(
                        data.location
                    )}
                </strong>

                <small>
                    ${escapeHTML(
                        data.country || ""
                    )}
                </small>

            </div>

        </div>


        <div class="ascii-rule"></div>


        <div class="ascii-weather-body">

            <div class="ascii-weather-art">

                <pre>${escapeHTML(
                    ascii
                )}</pre>

            </div>


            <div class="ascii-weather-values">

                <div class="ascii-data-row">
                    <span>DATA</span>
                    <strong>
                        ${formatWeatherDate(
                            data.date
                        )}
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>MÁXIMA</span>
                    <strong>
                        ${escapeHTML(
                            data.max
                        )} °C
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>MÍNIMA</span>
                    <strong>
                        ${escapeHTML(
                            data.min
                        )} °C
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>SENSAÇÃO MAX</span>
                    <strong>
                        ${escapeHTML(
                            data.apparent_max
                        )} °C
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>SENSAÇÃO MIN</span>
                    <strong>
                        ${escapeHTML(
                            data.apparent_min
                        )} °C
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>CHUVA</span>
                    <strong>
                        ${escapeHTML(
                            data.rain
                        )} %
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>PRECIPITAÇÃO</span>
                    <strong>
                        ${escapeHTML(
                            data.precipitation
                        )} mm
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>VENTO</span>
                    <strong>
                        ${escapeHTML(
                            data.wind
                        )} km/h
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>NASCER DO SOL</span>
                    <strong>
                        ${formatWeatherTime(
                            data.sunrise
                        )}
                    </strong>
                </div>

                <div class="ascii-data-row">
                    <span>PÔR DO SOL</span>
                    <strong>
                        ${formatWeatherTime(
                            data.sunset
                        )}
                    </strong>
                </div>

            </div>


            <div class="ascii-weather-summary">

                <div class="ascii-section-heading">
                    [ RESUMO DO DIA ]
                </div>

                <p>
                    ${escapeHTML(
                        result.response
                    )}
                </p>

            </div>

        </div>


        <div class="ascii-rule"></div>


        <div class="ascii-weather-status">

            <span>
                API://OPEN-METEO
            </span>

            <span>
                WEATHER MODULE [ ONLINE ]
            </span>

            <span>
                CONNECTION [ OK ]
            </span>

            <span>
                ${getCurrentTime()}
                // ${result.response_time}s
            </span>

        </div>
    `;


    message.appendChild(
        wrapper
    );

    messages.appendChild(
        message
    );


    requestAnimationFrame(
        () => {
            message.classList.add(
                "message-visible"
            );
        }
    );


    scrollToBottom();
}


// ======================================================
// CALCULADORA ASCII
// ======================================================

function addCalculatorMessage(result) {
    removeWelcome();


    const data =
        result.data;


    if (!data) {
        addMessage(
            "celene",
            result.response,
            result.response_time
        );

        return;
    }


    const message =
        document.createElement(
            "div"
        );

    message.classList.add(
        "message",
        "celene",
        "calculator-message"
    );


    const card =
        document.createElement(
            "section"
        );

    card.classList.add(
        "ascii-calculator"
    );


    card.innerHTML = `
        <div class="ascii-calculator-header">
            [ CALCULATOR UNIT ]
        </div>

        <div class="ascii-rule"></div>

        <div class="ascii-calculator-expression">
            INPUT &gt;
            ${escapeHTML(
                data.expression
            )}
        </div>

        <div class="ascii-calculator-result">
            OUTPUT &gt;
            ${escapeHTML(
                data.result
            )}
        </div>

        <div class="ascii-rule"></div>

        <div class="ascii-calculator-footer">
            STATUS [ OK ]
            //
            ${getCurrentTime()}
            //
            ${result.response_time}s
        </div>
    `;


    message.appendChild(
        card
    );

    messages.appendChild(
        message
    );


    requestAnimationFrame(
        () => {
            message.classList.add(
                "message-visible"
            );
        }
    );


    scrollToBottom();
}


// ======================================================
// RENDER
// ======================================================

function renderCeleneResponse(data) {
    if (!data) {
        addMessage(
            "celene",
            "SYSTEM ERROR // INVALID RESPONSE"
        );

        return;
    }

    switch (data.type) {

        case "weather":

            addWeatherMessage(
                data
            );

            break;


        case "calculator":

            addCalculatorMessage(
                data
            );

            break;


        case "code":

            addCodeMessage(
                data
            );

            break;


        case "weather_week":

            addMessage(
                "celene",
                data.response,
                data.response_time
            );

            break;


        case "error":

            addMessage(
                "celene",
                data.response ||
                "SYSTEM ERROR"
            );

            break;


        case "text":

        default:

            addMessage(
                "celene",
                data.response,
                data.response_time
            );

            break;
    }
}


// ======================================================
// CLASSIFY
// ======================================================

async function classifyMessage(
    message
) {
    const response =
        await fetch(
            "/api/classify",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message
                })
            }
        );


    if (!response.ok) {
        throw new Error(
            "CLASSIFY FAILURE"
        );
    }


    return await response.json();
}


// ======================================================
// TOOL
// ======================================================

async function sendToolMessage(
    message
) {
    showThinking();


    try {
        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message
                    })
                }
            );


        const data =
            await response.json();


        removeThinking();


        if (!response.ok) {
            throw new Error(
                data.response ||
                "TOOL FAILURE"
            );
        }


        renderCeleneResponse(
            data
        );
    }

    catch (error) {
        removeThinking();

        throw error;
    }
}


// ======================================================
// STREAMING MESSAGE
// ======================================================

function createStreamingMessage() {
    removeWelcome();


    const message =
        document.createElement(
            "div"
        );

    message.classList.add(
        "message",
        "celene"
    );


    const avatar =
        document.createElement(
            "div"
        );

    avatar.classList.add(
        "message-avatar"
    );

    avatar.textContent = "C";


    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.classList.add(
        "message-wrapper"
    );


    const content =
        document.createElement(
            "div"
        );

    content.classList.add(
        "message-content"
    );


    wrapper.appendChild(
        content
    );

    message.appendChild(
        avatar
    );

    message.appendChild(
        wrapper
    );

    messages.appendChild(
        message
    );


    requestAnimationFrame(
        () => {
            message.classList.add(
                "message-visible"
            );
        }
    );


    scrollToBottom();


    return {
        message,
        content,
        wrapper
    };
}


// ======================================================
// STREAMING
// ======================================================

async function streamFromCelene(
    message
) {
    const streaming =
        createStreamingMessage();


    const startTime =
        performance.now();


    try {
        const response =
            await fetch(
                "/api/chat/stream",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message
                    })
                }
            );


        if (!response.ok) {
            throw new Error(
                "STREAM FAILURE"
            );
        }


        if (!response.body) {
            throw new Error(
                "STREAM NOT AVAILABLE"
            );
        }


        const reader =
            response.body.getReader();


        const decoder =
            new TextDecoder(
                "utf-8"
            );


        while (true) {
            const {
                value,
                done
            } =
                await reader.read();


            if (done) {
                break;
            }


            if (!value) {
                continue;
            }


            const chunk =
                decoder.decode(
                    value,
                    {
                        stream: true
                    }
                );


            streaming.content.textContent +=
                chunk;


            scrollToBottom();
        }


        const responseTime =
            (
                (
                    performance.now()
                    - startTime
                ) / 1000
            ).toFixed(2);


        const meta =
            document.createElement(
                "div"
            );

        meta.classList.add(
            "message-meta"
        );


        meta.innerHTML = `
            <span>
                ${getCurrentTime()}
            </span>

            <span
                class="message-performance"
            >
                // ${responseTime}s
            </span>
        `;


        streaming.wrapper.appendChild(
            meta
        );
    }

    catch (error) {
        streaming.content.textContent =
            `SYSTEM ERROR // ${error.message}`;

        throw error;
    }
}


// ======================================================
// ENVIA PARA CELENE
// ======================================================

async function sendToCelene(
    message
) {
    setGenerating(true);


    try {
        const classification =
            await classifyMessage(
                message
            );


        if (
            classification.mode ===
            "tool"
        ) {
            await sendToolMessage(
                message
            );

            return;
        }


        if (
            classification.mode ===
            "stream"
        ) {
            await streamFromCelene(
                message
            );

            return;
        }


        throw new Error(
            "UNKNOWN PROCESSING MODE"
        );
    }

    catch (error) {
        removeThinking();


        console.error(
            "[CELENE]",
            error
        );


        addMessage(
            "celene",
            `SYSTEM ERROR // ${error.message}`
        );
    }

    finally {
        removeThinking();

        setGenerating(false);
    }
}


// ======================================================
// ENVIO
// ======================================================

function sendMessage() {
    if (isGenerating) {
        return;
    }


    const content =
        messageInput
        .value
        .trim();


    if (!content) {
        return;
    }


    addMessage(
        "user",
        content
    );


    messageInput.value = "";

    resizeTextarea();


    sendToCelene(
        content
    );
}


// ======================================================
// FORM
// ======================================================

messageForm.addEventListener(
    "submit",
    event => {
        event.preventDefault();

        sendMessage();
    }
);


// ======================================================
// ENTER
// ======================================================

messageInput.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            sendMessage();
        }
    }
);


// ======================================================
// AUTO RESIZE
// ======================================================

messageInput.addEventListener(
    "input",
    resizeTextarea
);


// ======================================================
// SUGESTÕES
// ======================================================

suggestions.forEach(
    suggestion => {
        suggestion.addEventListener(
            "click",
            () => {
                if (isGenerating) {
                    return;
                }


                messageInput.value =
                    suggestion
                    .innerText
                    .trim();


                messageInput.focus();

                resizeTextarea();
            }
        );
    }
);


// ======================================================
// NOVA CONVERSA
// ======================================================

if (newChat) {
    newChat.addEventListener(
        "click",
        () => {
            if (isGenerating) {
                return;
            }


            messages.innerHTML = `
                <div class="welcome-terminal">

                    <p>
                        CELENE&gt;
                        NEW SESSION INITIALIZED
                    </p>

                    <p>
                        CELENE&gt;
                        CORE ONLINE
                    </p>

                    <p>
                        CELENE&gt;
                        WAITING FOR INPUT_
                    </p>

                </div>
            `;


            messageInput.value = "";

            resizeTextarea();

            messageInput.focus();
        }
    );
}

// ======================================================
// RECONHECIMENTO DE VOZ
// ======================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

let recognition = null;
let isListening = false;


if (SpeechRecognition) {
    recognition =
        new SpeechRecognition();

    recognition.lang =
        "pt-BR";

    recognition.continuous =
        false;

    recognition.interimResults =
        true;


    recognition.onstart = () => {
        isListening = true;

        voiceButton.classList.add(
            "listening"
        );

        voiceButton.textContent =
            "REC";
    };


    recognition.onend = () => {
        isListening = false;

        voiceButton.classList.remove(
            "listening"
        );

        voiceButton.textContent =
            "MIC";
    };


    recognition.onerror = (
        event
    ) => {
        console.error(
            "[VOICE]",
            event.error
        );

        isListening = false;

        voiceButton.classList.remove(
            "listening"
        );

        voiceButton.textContent =
            "MIC";
    };


    recognition.onresult = (
        event
    ) => {
        let transcript = "";

        for (
            let i =
                event.resultIndex;
            i <
                event.results.length;
            i++
        ) {
            transcript +=
                event.results[i][0]
                    .transcript;
        }

        messageInput.value =
            transcript;

        resizeTextarea();


        const lastResult =
            event.results[
                event.results.length - 1
            ];

        if (
            lastResult.isFinal
        ) {
            messageInput.value =
                transcript.trim();

            resizeTextarea();
        }
    };
}


if (voiceButton) {
    voiceButton.addEventListener(
        "click",
        () => {
            if (!recognition) {
                addMessage(
                    "celene",
                    "Reconhecimento de voz não está disponível neste navegador."
                );

                return;
            }


            if (isListening) {
                recognition.stop();

                return;
            }


            recognition.start();
        }
    );
}

// ======================================================
// CODE CARD
// ======================================================

function addCodeMessage(result) {
    removeWelcome();

    const data = result.data;

    if (!data) {
        addMessage(
            "celene",
            result.response,
            result.response_time
        );

        return;
    }

    const message =
        document.createElement("div");

    message.classList.add(
        "message",
        "celene",
        "code-message"
    );

    const card =
        document.createElement("section");

    card.classList.add(
        "ascii-code-card"
    );

    // ------------------------------------------
    // LINHAS DO CÓDIGO
    // ------------------------------------------

    const codeLines =
        String(data.code)
        .split("\n");

    const numberedCode =
        codeLines
        .map(
            (line, index) => {
                const number =
                    String(index + 1)
                    .padStart(2, "0");

                return `
                    <div class="code-line">
                        <span class="code-line-number">
                            ${number}
                        </span>

                        <span class="code-line-content">
                            ${escapeHTML(line)}
                        </span>
                    </div>
                `;
            }
        )
        .join("");

    card.innerHTML = `
        <div class="ascii-code-header">

            <div>
                <span class="ascii-code-label">
                    CODE://GENERATED
                </span>

                <h3>
                    ${escapeHTML(data.title)}
                </h3>
            </div>

            <div class="ascii-code-status">
                [ READY ]
            </div>

        </div>


        <div class="ascii-rule"></div>


        <div class="ascii-code-info">

            <div>
                <span>FILE</span>

                <strong>
                    ${escapeHTML(data.filename)}
                </strong>
            </div>

            <div>
                <span>LANGUAGE</span>

                <strong>
                    ${escapeHTML(
                        data.language
                            .toUpperCase()
                    )}
                </strong>
            </div>

            <div>
                <span>LINES</span>

                <strong>
                    ${codeLines.length}
                </strong>
            </div>

        </div>


        <div class="ascii-rule"></div>


        <div class="ascii-code-description">
            ${escapeHTML(
                data.description
            )}
        </div>


        <div class="ascii-code-window">

            <div class="ascii-code-window-header">

                <span>
                    ${escapeHTML(data.filename)}
                </span>

                <span>
                    ${escapeHTML(
                        data.language
                    )}
                </span>

            </div>


            <div class="ascii-code-content">
                ${numberedCode}
            </div>

        </div>


        <div class="ascii-code-actions">

            <button
                type="button"
                class="code-copy-button"
            >
                [ COPY ]
            </button>

            <span>
                STATUS://GENERATED
            </span>

            <span>
                ${getCurrentTime()}
                // ${result.response_time}s
            </span>

        </div>
    `;


    // ==========================================
    // BOTÃO COPY
    // ==========================================

    const copyButton =
        card.querySelector(
            ".code-copy-button"
        );

    copyButton.addEventListener(
        "click",
        async () => {
            try {
                await navigator.clipboard.writeText(
                    data.code
                );

                copyButton.textContent =
                    "[ COPIED ]";

                setTimeout(
                    () => {
                        copyButton.textContent =
                            "[ COPY ]";
                    },
                    1500
                );

            } catch (error) {
                console.error(
                    "[COPY]",
                    error
                );

                copyButton.textContent =
                    "[ ERROR ]";
            }
        }
    );


    message.appendChild(card);

    messages.appendChild(message);


    requestAnimationFrame(
        () => {
            message.classList.add(
                "message-visible"
            );
        }
    );


    scrollToBottom();
}
// ======================================================
// INICIALIZAÇÃO
// ======================================================

messageInput.focus();


// Monitor inicial
updateSystemMonitor();


// Atualiza CPU / GPU / RAM / DISCO
// a cada 1 segundo
setInterval(
    updateSystemMonitor,
    1000
);