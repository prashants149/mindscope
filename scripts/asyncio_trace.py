import sys
import asyncio

print("1. Creating loop...", flush=True)
loop = asyncio.new_event_loop()
print("2. Created loop:", loop, flush=True)

async def test_coro():
    print("3. Inside test_coro", flush=True)
    return 42

print("4. Calling run_until_complete...", flush=True)
res = loop.run_until_complete(test_coro())
print("5. Result:", res, flush=True)
loop.close()
print("6. Done!", flush=True)
