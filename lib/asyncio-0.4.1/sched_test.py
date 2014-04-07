ximport tulip


def reader(s):
    res = yield from s.read(1)
    while res:
        print ('got data:', res)
        res = yield from s.read(1)


def main(stream):
    stream2 = tulip.StreamReader()

    # start separate task
    t = tulip.async(reader(stream2))

    while 1:
        data = yield from stream.read(1)
        print ('received data:', data)
        if data == b'0':
            break

        stream2.feed_data(data)

    stream2.feed_eof()

    #yield from t


if __name__ == '__main__':
    loop = tulip.get_event_loop()

    stream = tulip.StreamReader()
    stream.feed_data(b'1234567890')
    try:
        loop.run_until_complete(main(stream))
    except KeyboardInterrupt:
        pass
