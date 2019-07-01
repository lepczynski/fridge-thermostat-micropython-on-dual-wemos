import webrepl
import gc

gc.collect()

print('Lighthouse boot start...')

def setup_lighthouse_ap():
    print('lighthouse setting up AP for WebRepl...')

    import network as n
    ap = n.WLAN(n.AP_IF)
    try:
        config_lighthouse_AP_file = open('properties.lighthouse.AP.txt', 'r')
        config_lighthouse_AP = [ x.rstrip() for x in config_lighthouse_AP_file.readlines() ]

        ap.config(essid=config_lighthouse_AP[0], password=config_lighthouse_AP[1])  # channel=11
    except OSError as e:
        print('ERROR lighthouse.boot while retrieveing ap password file: ', e)
        print('Fall-back password in use!')
        ap.config(essid='fridge-lighthouse', password='fallback fridge password')  # channel=11
    finally:
        config_lighthouse_AP_file.close()

    ap.active(True)
    print('AP status: ', ap.status())


setup_lighthouse_ap()


def connect_to_engine():
    import network as n
    station = n.WLAN(n.STA_IF)
    if not station.isconnected():
        print('lighthouse connecting to the engine...')
        station.active(True)
        station.config(dhcp_hostname='lodowka-lighthouse')
        
        try:
            config_engine_AP_file = open('properties.engine.AP.txt','r')
            config_engine_AP = [ x.rstrip() for x in config_engine_AP_file.readlines() ]
            station.connect(config_engine_AP[0], config_engine_AP[1])
        except OSError as e:
            print('ERROR engine.boot while retrieveing engine password file: ', e)
            print('proceeding... Please WebRepl into lighthouse AP and fix config file!')
        finally:
            config_engine_AP_file.close()


        while not station.isconnected():
            pass
    print('lighthouse station config:', station.ifconfig())
    print('rssi: ', station.status('rssi'))


webrepl.start()
gc.collect()

try:
    connect_to_engine()
    gc.collect()
except OSError as e:
    print('ERROR lighthouse.boot: connect_to_engine: ', e)
    import time
    import machine
    time.sleep(10)
    machine.reset()

print('lighthouse booting complete.')
