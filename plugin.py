# Bluetooth Presence Python Plugin for Domoticz
#
# Authors: mvdklip
#

"""
<plugin key="BluetoothPresence" name="Bluetooth Presence" author="mvdklip" version="0.2.2" >
    <description>
        <h2>Bluetooth presence plugin</h2><br/>
        Detects if a given bluetooth MAC address is within reach of Domoticz<br/>
    </description>
    <params>
        <param field="Address" label="Bluetooth MAC Address" width="200px" required="true"/>
        <param field="Mode3" label="Cooldown in seconds" width="75px" required="true">
            <options>
                <option label="5 min" value="10"/>
                <option label="10 min" value="20"/>
                <option label="15 min" value="30"/>
                <option label="30 min" value="60" default="true"/>
                <option label="60 min" value="120"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import queue
import time
import threading
import bluetooth


class BasePlugin:
    enabled = False
    lastSeen = 0
    
    def __init__(self):
        self.messageQueue = queue.Queue()
        self.messageThread = threading.Thread(name="QueueThread", target=BasePlugin.handleMessage, args=(self,))

    def handleMessage(self):
        Domoticz.Debug("Entering message handler")
        while True:
            Message = self.messageQueue.get(block=True)
            try:
                if Message is None:
                    Domoticz.Debug("Exiting message handler")
                    break
                elif (Message["Type"] == "Ping"):
                    Domoticz.Debug("handleMessage: '"+Message["Type"]+" "+Message["Address"]+"'.")
                    if (bluetooth.lookup_name(Message['Address']) is not None):
                        Domoticz.Debug("Pong!")
                        self.lastSeen = 0
                else:
                    raise Exception("Unknown message type: "+Message["Type"])
            except Exception as err:
                Domoticz.Error("handleMessage: "+str(err))
            finally:
                self.messageQueue.task_done()
    
    def onStart(self):
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        if len(Devices) < 1:
            Domoticz.Device(Name="Presence", Unit=1, TypeName='Switch', Image=18).Create()
        if Devices[1].nValue == 0:
            self.lastSeen = int(Parameters["Mode3"])
        self.messageThread.start()
        Domoticz.Heartbeat(30)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called %d" % self.lastSeen)
        if self.lastSeen >= int(Parameters["Mode3"]):
            Domoticz.Debug("Device gone for more than "+Parameters["Mode3"]+" beats; updating presence")
            newValue=0
        else:
            Domoticz.Debug("Device present")
            newValue=1
        if newValue != Devices[1].nValue:
            Devices[1].Update(nValue=newValue, sValue="")

        self.messageQueue.put({"Type":"Ping", "Address":Parameters['Address']})
        self.lastSeen += 1

    def onStop(self):
        # Signal queue thread to exit
        self.messageQueue.put(None)
        Domoticz.Debug("Clearing message queue...")
        self.messageQueue.join()

        # Wait until queue thread has exited
        Domoticz.Debug("Threads still active: "+str(threading.active_count())+", should be 1.")
        while (threading.active_count() > 1):
            for thread in threading.enumerate():
                if (thread.name != threading.current_thread().name):
                    Domoticz.Log("'"+thread.name+"' is still running, waiting otherwise Domoticz will abort on plugin exit.")
            time.sleep(1.0)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
