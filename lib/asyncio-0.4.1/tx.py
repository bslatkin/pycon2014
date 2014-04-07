import asyncio

def main():
    loop = asyncio.get_event_loop()
    fut = asyncio.Future()
    try:
        raise ValueError()
    except Exception as err:
        fut.set_exception(err)
    fut = None
    print('-'*20)
    loop.run_until_complete(asyncio.sleep(1))

main()
