from pathlib import Path
from time import perf_counter

from flask import (
    Flask,
    Response,
    jsonify,
    request,
    send_from_directory,
    stream_with_context,
)

from app.core.brain import Brain
from app.core.tool_detector import ToolDetector
from app.services.memory import load_memory
from app.services.system_monitor import SystemMonitor


# ======================================================
# CAMINHOS
# ======================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

INTERFACE_DIR = (
    BASE_DIR
    / "interface"
)


# ======================================================
# FLASK
# ======================================================

app = Flask(
    __name__,
    static_folder=str(
        INTERFACE_DIR
    ),
    static_url_path=""
)


# ======================================================
# CELENE
# ======================================================

memory = load_memory()

brain = Brain(
    memory
)


# ======================================================
# MONITOR DO SISTEMA
# ======================================================

system_monitor = SystemMonitor()


# ======================================================
# INTERFACE
# ======================================================

@app.route("/")
def index():
    return send_from_directory(
        str(INTERFACE_DIR),
        "index.html"
    )


# ======================================================
# STATUS DA CELENE
# ======================================================

@app.route(
    "/api/status",
    methods=["GET"]
)
def status():
    return jsonify({
        "status": "online",
        "assistant": "Celene",
        "version": "0.5",
        "model": "celene"
    })


# ======================================================
# STATUS DO COMPUTADOR
# ======================================================

@app.route(
    "/api/system",
    methods=["GET"]
)
def system_status():
    try:
        data = (
            system_monitor
            .get_all()
        )

        return jsonify(
            data
        )

    except Exception as error:
        print(
            "[SYSTEM] Erro ao obter "
            f"dados: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível obter "
                "os dados do sistema."
            )
        }), 500


# ======================================================
# CHAT NORMAL / FERRAMENTAS
# ======================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():
    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "type": "error",
            "response": (
                "Nenhum dado foi recebido."
            ),
            "data": None,
            "response_time": 0
        }), 400

    message = data.get(
        "message",
        ""
    )

    if not isinstance(
        message,
        str
    ):
        return jsonify({
            "type": "error",
            "response": (
                "A mensagem precisa "
                "ser um texto."
            ),
            "data": None,
            "response_time": 0
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "type": "error",
            "response": (
                "A mensagem não pode "
                "estar vazia."
            ),
            "data": None,
            "response_time": 0
        }), 400

    try:
        result = brain.think(
            message
        )

        print(
            "[SERVER] Resposta do Brain:"
        )

        print(
            result
        )

        return jsonify(
            result
        )

    except Exception as error:
        print(
            "[SERVER] Erro ao processar "
            f"mensagem: {error}"
        )

        return jsonify({
            "type": "error",
            "response": (
                "Ocorreu um erro interno "
                "ao processar sua mensagem."
            ),
            "data": None,
            "response_time": 0
        }), 500


# ======================================================
# CLASSIFICAÇÃO
# ======================================================

@app.route(
    "/api/classify",
    methods=["POST"]
)
def classify():
    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "mode": "error"
        }), 400

    message = data.get(
        "message",
        ""
    )

    if not isinstance(
        message,
        str
    ):
        return jsonify({
            "mode": "error"
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "mode": "error"
        }), 400

    # ----------------------------------
    # FERRAMENTA PENDENTE
    # ----------------------------------

    if brain.pending_tool:
        return jsonify({
            "mode": "tool"
        })

    # ----------------------------------
    # CONTINUAÇÃO DE CLIMA
    # ----------------------------------

    if (
        brain.last_tool == "weather"
        and brain.looks_like_location(
            message
        )
    ):
        return jsonify({
            "mode": "tool"
        })

    # ----------------------------------
    # TOOL DETECTOR LOCAL
    # ----------------------------------

    tool = ToolDetector.detect(
        message
    )

    if tool:
        return jsonify({
            "mode": "tool"
        })

    # ----------------------------------
    # CONVERSA NORMAL
    # ----------------------------------

    return jsonify({
        "mode": "stream"
    })


# ======================================================
# STREAMING
# ======================================================

@app.route(
    "/api/chat/stream",
    methods=["POST"]
)
def chat_stream():
    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "error": (
                "Nenhum dado recebido."
            )
        }), 400

    message = data.get(
        "message",
        ""
    )

    if not isinstance(
        message,
        str
    ):
        return jsonify({
            "error": (
                "Mensagem inválida."
            )
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "error": (
                "Mensagem vazia."
            )
        }), 400

    history = (
        brain
        .conversation
        .get_recent(
            limit=6
        )
    )

    start = perf_counter()

    @stream_with_context
    def generate():
        full_response = ""

        try:
            for chunk in (
                brain
                .ai
                .stream_generate(
                    message=message,
                    history=history
                )
            ):
                full_response += chunk

                yield chunk

        except Exception as error:
            print(
                "[STREAM] Erro durante "
                f"streaming: {error}"
            )

            yield (
                "\nSYSTEM ERROR // "
                "STREAM INTERRUPTED"
            )

        finally:
            response_time = (
                perf_counter()
                - start
            )

            if full_response:
                brain.conversation.add(
                    author="user",
                    content=message
                )

                brain.conversation.add(
                    author="celene",
                    content=full_response,
                    response_time=response_time
                )

    return Response(
        generate(),
        content_type=(
            "text/plain; "
            "charset=utf-8"
        )
    )


# ======================================================
# ARQUIVOS ESTÁTICOS
# ======================================================

@app.route(
    "/<path:filename>"
)
def static_files(
    filename
):
    return send_from_directory(
        str(INTERFACE_DIR),
        filename
    )


# ======================================================
# START
# ======================================================

if __name__ == "__main__":
    print()
    print(
        "=" * 52
    )

    print(
        "                  CELENE API"
    )

    print(
        "=" * 52
    )

    print()

    print(
        "[SERVER] Interface:"
    )

    print(
        "         "
        "http://127.0.0.1:5000"
    )

    print()

    print(
        "[SERVER] Celene status:"
    )

    print(
        "         "
        "http://127.0.0.1:5000/api/status"
    )

    print()

    print(
        "[SERVER] System monitor:"
    )

    print(
        "         "
        "http://127.0.0.1:5000/api/system"
    )

    print()

    print(
        "[SERVER] Chat:"
    )

    print(
        "         "
        "POST /api/chat"
    )

    print()

    print(
        "[SERVER] Classify:"
    )

    print(
        "         "
        "POST /api/classify"
    )

    print()

    print(
        "[SERVER] Streaming:"
    )

    print(
        "         "
        "POST /api/chat/stream"
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )