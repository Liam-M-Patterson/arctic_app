import asyncio
from threading import Thread


def side_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def display(text):
    await asyncio.sleep(5)
    print("echo:", text)
    return text == "exit"



loop = asyncio.new_event_loop()
thread = Thread(target=side_thread, args=(loop,), daemon=True)
thread.start()


while True:
  text = input("enter text: ")
  asyncio.run_coroutine_threadsafe(display(text), loop)