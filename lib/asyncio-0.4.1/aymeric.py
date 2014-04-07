import tulip

messages = tulip.DataBuffer()
messages.feed_data('a message')

@tulip.task
def print_messages():
    while True:
        print((yield from messages.read()))

print_task = print_messages()

loop = tulip.get_event_loop()
loop.call_later(1, print_task.cancel)
loop.call_later(2, messages.feed_eof)
loop.call_later(3, loop.stop)
loop.run_forever()
