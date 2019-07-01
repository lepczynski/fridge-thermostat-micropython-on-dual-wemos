# Lodowka-engine
# by Lepi 2019
# role: SERVER
# ip: 192.168.1.44

from machine import Pin
import gc


DOOR_PIN = 5 # D1
ENGINE_PIN = 2 # D4
TCP_PORT = 55555

door_check_interval = 200


# def doorman(p):
#     print('IRQ doorman here, event: ', p)
#
# _door.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=doorman)

_door = Pin(DOOR_PIN, Pin.IN, Pin.PULL_UP)  # Pin.PULL_DOWN / Pin.PULL_NONE
_engine = Pin(ENGINE_PIN, Pin.OUT)
_engine.off()


def door():
    return not _door.value()


def on():
    _engine.on()


def off():
    _engine.off()


def engine():
    print('Engine is %s.' % (not _engine.value()))
    return not _engine.value()


def server(port, max_clients=5):
    import utime, gc
    import usocket as socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Opening a socket at port %d..." % port)
    print('Binding socket...')
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    print('Socket is bound! :>')

    sock.listen(max_clients)
    print("Socket is listening at %d..." % port)

    connected_socket, client_address = sock.accept()
    print("Socket connected from %s:%d." % (client_address[0], client_address[1]))

    door_check_last = utime.ticks_ms()

    while 1:
        now = utime.ticks_ms()
        
        data = connected_socket.recv(1024).decode()
        if not data:
            break
        print("Received from client: [%s]" % str(data))

        # toDo: case switch or sth
        if str(data) == 'on':
            on()
            connected_socket.sendall('Engine on!'.encode())
        elif str(data) == 'off':
            off()
            connected_socket.sendall('Engine off.'.encode())
        elif str(data) == 'door':
            connected_socket.sendall(str(door()).encode())
        elif utime.ticks_diff(now, door_check_last) > door_check_interval:
            print('Checking the door...')
            door_check_last = now
            door_state = door()
            connected_socket.sendall(('on' if door_state else 'off').encode())

        gc.collect()

    print("Closing socket...")
    sock.close()
    print("Socket closed!")

def loop():
    while 1:
        try:
            gc.collect()
            server(TCP_PORT)
        except OSError as e:
            print('ERROR: engine.main: server:', e)
            import time
            import machine
            time.sleep(10)
            machine.reset()


if __name__ == '__main__':
    loop()
