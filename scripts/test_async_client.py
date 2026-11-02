import asyncio
import httpx
from fastapi import FastAPI

a = FastAPI()

@a.get("/")
async def home():
    return {"ok": True}

async def main():
    print("In main...", flush=True)
    transport = httpx.ASGITransport(app=a)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        print("Calling get...", flush=True)
        r = await c.get("/")
        print("Async result:", r.json(), flush=True)

asyncio.run(main())

