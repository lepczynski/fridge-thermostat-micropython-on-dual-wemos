# Lodowka-lighthouse
# by Lepi 2019
# role: CLIENT
# ip: 192.168.1.43

import time
import machine
import neopixel
import gc


TEMPERATURE_PIN = 2 # D4
LEDS_PIN = 0 # D3
LEDS_NUM = 1
TCP_ADDR = '192.168.1.44'
TCP_PORT = 55555

temp_check_interval = 1000 # toDo: after dev change to ~60s?
temp_min = 4
temp_max = 2

_pixels = neopixel.NeoPixel(machine.Pin(LEDS_PIN), LEDS_NUM)


def read_temp():
    import time
    import machine
    import onewire
    import ds18x20
    dat = machine.Pin(TEMPERATURE_PIN)
    # create the onewire object
    ds = ds18x20.DS18X20(onewire.OneWire(dat))
    # scan for devices on the bus
    roms = ds.scan()
    # print('found devices:', roms)
    # print('temperature:', end=' ')
    ds.convert_temp()
    time.sleep_ms(750)
    temp = ds.read_temp(roms[0])
    # print(temp)
    return temp 


def wheel(pos):
    if pos < 0 or pos > 255:
        return 0, 0, 0
    if pos < 85:
        return 255 - pos * 3, pos * 3, 0
    if pos < 170:
        pos -= 85
        return 0, 255 - pos * 3, pos * 3
    pos -= 170
    return pos * 3, 0, 255 - pos * 3


def leds_rainbow():
    for i in range(LEDS_NUM):
        rc_index = (i * 256 // LEDS_NUM)
        _pixels[i] = wheel(rc_index & 255)
    _pixels.write()


def leds_uni_random():
    import random
    r = random.getrandbits(8)
    g = random.getrandbits(8)
    b = random.getrandbits(8)

    for i in range(LEDS_NUM):
        _pixels[i] = (r, g, b)
    _pixels.write()


def leds_random():
    import random
    for i in range(LEDS_NUM):
        _pixels[i] = (random.getrandbits(8), random.getrandbits(8), random.getrandbits(8))
    _pixels.write()


def leds_black():
    for i in range(LEDS_NUM):
        _pixels[i] = (0, 0, 0)
    _pixels.write()


def client(host, port):
    import utime, gc
    import usocket as socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Connecting socket to %s:%d..." % (host, port))
    sock.connect((host, port))
    print("Socket connected.")

    temp_check_last = utime.ticks_ms()

    # toDO: rather no error loop and try-catch if connection lost
    while 1:
        now = utime.ticks_ms()

        data = sock.recv(1024).decode()
        print("Received from server: [%s]" % str(data))

        if str(data) == 'on':
            leds_random()
            sock.sendall('Lights on!'.encode())
        elif str(data) == 'off':
            leds_black()
            sock.sendall('Lights off.'.encode())


        if utime.ticks_diff(now, temp_check_last) > temp_check_interval:
            temp_check_last = now
            temp = read_temp()

            if temp > temp_max:
                sock.sendall('on'.encode())
            elif temp < temp_min:
                sock.sendall('off'.encode())

        gc.collect()


    sock.close()
    print("Client socket closed.")


def loop():
    while 1:
        try:
            client(TCP_ADDR, TCP_PORT)
        except OSError as e:
            print('ERROR: lighthouse.main: client:', e)
            import time
            import machine
            time.sleep(10)
            machine.reset()


if __name__ == '__main__':
    loop()
