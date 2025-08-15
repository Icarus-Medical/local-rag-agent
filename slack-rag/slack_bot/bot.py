import os, asyncio, httpx
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]  # App-level (connections:write)
RAG_API_URL     = os.getenv("RAG_API_URL", "http://127.0.0.1:8000/answer")

app = AsyncApp(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
async def on_mention(body, say):
    evt = body["event"]
    user_text = evt.get("text", "")
    channel = evt["channel"]
    placeholder = await say("Working on it…")
    ts = placeholder["ts"]

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(RAG_API_URL, json={"text": user_text})
        data = resp.json()

    await app.client.chat_update(channel=channel, ts=ts, text=data.get("text", "(no answer)"))

async def main():
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
