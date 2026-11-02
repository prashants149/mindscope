import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
print("BEFORE ASYNCIO RUN", flush=True)
async def m():
    print("INSIDE M", flush=True)
asyncio.run(m())
print("AFTER ASYNCIO RUN", flush=True)
