import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + "/../")

from droidbot.input_event import *
from droidbot.device import Device
from droidbot.app import App


device_serial="14131FDF600073"
app_path = "/root/documents/droidbot-new/a2dp_2/a2dp.Vol_169.apk"
droid_output = "/root/documents/droidbot-new/a2dp/"

Confiot_output = "/root/documents/droidbot-new/a2dp/Confiot"
event_file = BASE_DIR + "/event.json"


class Confiot:
    def __init__(self) -> None:
        self.device = Device(device_serial=device_serial, ignore_ad=True)
        self.app = App(app_path=app_path, output_dir=Confiot_output)
        self.start_state = None

    def device_connect(self):
        # device.connect()
        self.device.install_app(self.app)
        self.device.start_app(self.app)

        with open(event_file, "r") as f:
            event_dict = json.load(f)["event"]
            event = InputEvent.from_dict(event_dict)
            print(event)
            event.send(self.device)

    def parse_utg(self) -> tuple:
        utg_dict = {}
        utg_nodes = []
        utg_edges = []

        with open(droid_output + "/utg.js", "r") as f:
            utg_content = f.read()
            if(utg_content != ''):
                utg_content = utg_content.replace("var utg = ", '')
                utg_content = utg_content.replace(";", "")
                utg_dict = json.loads(utg_content)
                utg_nodes = utg_dict["nodes"]
                utg_edges = utg_dict["edges"]

                for node in utg_nodes:
                    node_activity = (node["package"] + node["activity"]).replace("}", "")
                    if(node_activity == utg_dict["app_main_activity"]):
                        self.start_state = node["state_str"]
                        break

        if(utg_nodes != [] and utg_edges != [] and self.start_state is not None):
            print("[DBG]: Start state: " + self.start_state)
        else:
            print("[ERR]: Cannot find start state")

        return utg_nodes, utg_edges



    def goto_state(self, state:str):
        pass



if __name__ == "__main__":
    confiot = Confiot()
    #confiot.device_connect()
    confiot.parse_utg()


