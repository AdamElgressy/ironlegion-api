from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = {}  # client_id connection val-pair.

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    #
    # async def send_personal_message(self, message: str, websocket: WebSocket):
    #     await websocket.send_text(message)
    #
    # async def broadcast(self, message: str):
    #     for connection in self.active_connections:
    #         await connection.send_text(message)

    def get(self, client_id: int) -> WebSocket:
        return self.active_connections[client_id]


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


#
# @app.get("/{client_id}/start")
# async def start():
#     return websocket_start()


@app.get("/{client_id}/stop")
async def stop(client_id):
    return _stop(client_id)


@app.post("/")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # handle message
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


# add avatar middleware
# add client middleware
async def _stop(client_id, avatar_id):
    client = get_client(client_id)
    await client.stop(avatar_id)


