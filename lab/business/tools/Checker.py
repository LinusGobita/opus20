import os

def check_connection_opus20(opus20):
#    opus20.request_supported_channels()
    try:
        opus20.connect()
        status = opus20.connected
        opus20.disconnect()
    except ValueError:
        print("can not connect")

    print(f"connectet {opus20.host} is {status}")

    return status

""""    
    #response = os.system("ping -c 1 " + opus20.host)

    opus20.request_device_status()
    response = opus20.connected

    if response == True:
        opus20.disconnect()

    print(f" {response} ----------")

    return response
"""