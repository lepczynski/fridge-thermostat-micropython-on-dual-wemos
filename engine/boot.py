import webrepl
import gc
import machine

gc.collect()

print('Engine boot start...')

def setup_engine_ap():
    print('engine setting up AP for the lighthouse and WebRepl...')
    
    import network as n
    ap = n.WLAN(n.AP_IF)
    try:
        config_engine_AP_file = open('properties.engine.AP.txt','r')
        config_engine_AP = [ x.rstrip() for x in config_engine_AP_file.readlines() ]

        ap.config(essid=config_engine_AP[0], password=config_engine_AP[1])  # channel=11 ?
    except OSError as e:
        print('ERROR engine.boot while retrieveing ap config file: ', e)
        print('Fall-back password in use!')
        ap.config(essid='fridge-engine', password='fallback fridge password')  # channel=11 ?
    finally:
        config_engine_AP_file.close()

    ap.active(True)
    print('AP status: ', ap.status())

    # fixMe:  'ValueError: unknown status param'
    # print('AP stations: ', ap.status('stations'))


try:
    setup_engine_ap()
    gc.collect()
except OSError as e:
    print('ERROR engine.boot: setup_engine_AP: ', e)
    import time
    import machine
    time.sleep(10)
    machine.reset()


def connect_to_WiFi():
    import network as n
    import machine
    station = n.WLAN(n.STA_IF)
    
    if not station.isconnected():
        print('engine connecting to local network...')
        station.active(True)
        station.config(dhcp_hostname='fridge-engine')
        try:
            config_WiFi_file = open('properties.WiFi.txt','r')
            config_WiFi = [ x.rstrip() for x in config_WiFi_file.readlines() ]

            station.connect(config_WiFi[0], config_WiFi[1])
        except OSError as e:
            print('ERROR engine.boot while retrieveing lepi password file: ', e)
            machine.reset()
        finally:
            lepi_pass_file.close()
    
        while not station.isconnected():
            pass
    print('engine station config:', station.ifconfig())
    print('rssi: ', station.status('rssi'))

webrepl.start()

connect_to_WiFi()

gc.collect()

print('engine booting complete.')
