import argparse
import websocket

def on_message(ws, message):
    print("📩 New message:", message)

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 Connection closed")

def on_open(ws):
    print("✅ Connected to Reporter Service")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="JWT token")
    parser.add_argument("--url", default="ws://localhost:8103/ws", help="WebSocket URL")
    args = parser.parse_args()

    ws_url = f"{args.url}?token={args.token}"
    print(f"Connecting to {ws_url} ...")

    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()