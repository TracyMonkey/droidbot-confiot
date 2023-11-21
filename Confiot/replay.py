import json
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + "/../")

from droidbot.input_event import *
from droidbot.device import Device
from droidbot.app import App
from util import DirectedGraph, Node, Edge

device_serial = "17291JECB10652"
app_path = "/Users/tracy/Documents/workspaces/appUI/droidbot/apks/com.xiaomi.smarthome"
droid_output = "/Users/tracy/Documents/github/droidbot/mihome/pixel5"

Confiot_output = "/Users/tracy/Documents/github/droidbot/Confiot"


class Confiot:

    def __init__(self) -> None:
        self.device: Device = None
        self.app: App = None
        self.utg_graph: DirectedGraph = None
        # {"event_str": event_json_path}
        self.events = {}

    def device_connect(self):
        self.device = Device(device_serial=device_serial, ignore_ad=True)
        self.app = App(app_path=app_path, output_dir=Confiot_output)
        # device.connect()
        self.device.install_app(self.app)

    def device_screenshot(self, tag):
        local_image_path = Confiot_output + "/screenshot_%s.png" % tag
        remote_image_path = "/sdcard/screen_%s.png" % tag
        self.device.adb.shell("screencap -p %s" % remote_image_path)
        self.device.pull_file(remote_image_path, local_image_path)
        self.device.adb.shell("rm %s" % remote_image_path)

    def device_stop_app(self):
        try:
            stack = self.device.get_current_activity_stack()
            current_package = None
            for acts in stack:
                acts_package = acts.split("/")[0]
                if (acts_package != current_package and acts_package != "com.android.systemui" and acts_package != ""):
                    if (acts_package == self.app.get_package_name()):
                        break
                    current_package = acts_package
                    self.device.adb.shell("am force-stop " + current_package)
            stop_app_intent = self.app.get_stop_intent()
            go_back_event = IntentEvent(stop_app_intent)
            go_back_event.send(self.device)
        except:
            print("[ERR]: Cannot stop app")

    def device_to_state(self, target_state: str):
        event_str_path = []
        path = self.utg_graph.find_shortest_path(self.utg_graph.start_node, target_state)
        if (path):
            current_node = path[0]
            for node in path[1:]:
                event_str_path.append(self.utg_graph.edges_dict[current_node.name][node.name][0])
                current_node = node

        self.device_stop_app()
        self.device.start_app(self.app)
        # waiting for app start
        time.sleep(5)
        for estr in event_str_path:
            time.sleep(2)
            if (estr in self.events):
                with open(self.events[estr], "r") as f:
                    event_dict = json.load(f)["event"]
                    event = InputEvent.from_dict(event_dict)
                    print("[DBG]: Action: " + estr)
                    print(event)
                    event.send(self.device)
            else:
                print("[ERR]: Wrong event path: ", event_str_path)
                break

        self.device.get_current_state()
        print("[DBG]: Finish")

    def parse_event(self):
        events_path = droid_output + "/events/"
        events_json = os.listdir(events_path)
        for j in events_json:
            with open(events_path + j, "r") as f:
                try:
                    event_str = json.load(f)["event_str"]
                    if (event_str != ''):
                        self.events[event_str] = events_path + j
                except Exception as e:
                    print(f"[ERR]: Failed to parse the event file `{j}`\n" + str(e))

    def parse_utg(self) -> DirectedGraph:
        self.utg_graph = DirectedGraph()
        utg_nodes = {}

        utg_dict = {}
        nodes_dict = []
        edges_dict = []

        with open(droid_output + "/utg.js", "r") as f:
            utg_content = f.read()
            if (utg_content != ''):
                utg_content = utg_content.replace("var utg = ", '')
                utg_content = utg_content.replace(";", "")
                utg_dict = json.loads(utg_content)
                nodes_dict = utg_dict["nodes"]
                edges_dict = utg_dict["edges"]

                for node in nodes_dict:
                    activity = (node["package"] + node["activity"]).replace("}", "")
                    if (activity == utg_dict["app_main_activity"]):
                        self.utg_graph.start_node = node["state_str"]
                        break

        if (nodes_dict != [] and edges_dict != [] and self.utg_graph.start_node is not None):
            print("[DBG]: Start state: " + self.utg_graph.start_node)
        else:
            print("[ERR]: Cannot find start state")
            return None

        # parse utg with DirectedGraph
        for n in nodes_dict:
            self.utg_graph.add_node(Node(n["state_str"]))
            utg_nodes[n["state_str"]] = self.utg_graph.nodes[-1]

        for e in edges_dict:
            event_strs = [eve["event_str"] for eve in e["events"]]
            self.utg_graph.add_edge(Edge(utg_nodes[e["from"]], utg_nodes[e["to"]], event_strs))

        return self.utg_graph
    



def test_goto_state():
    confiot = Confiot()
    confiot.device_connect()

    confiot.parse_event()
    # print(confiot.events)
    confiot.parse_utg()

    while (1):
        target_str = input("state: ")
        if (target_str == '\n' or target_str == ''):
            confiot.device_stop_app()
            break
        confiot.device_to_state(target_str)


def test_stop_app():
    confiot = Confiot()
    confiot.device_connect()

    confiot.device_stop_app()


def test_do_event():
    confiot = Confiot()
    confiot.device_connect()
    confiot.parse_event()

    confiot.device_stop_app()
    confiot.device.start_app(confiot.app)
    # waiting for app start
    time.sleep(5)
    count = 0

    while (1):
        event_str = input("event_str: ")
        if (event_str == '\n' or event_str == ''):
            confiot.device_stop_app()
            break

        with open(confiot.events[event_str], "r") as f:
                    event_dict = json.load(f)["event"]
                    event = InputEvent.from_dict(event_dict)
                    print("[DBG]: Action: " + event_str)
                    print(event)
                    event.send(confiot.device)
                    time.sleep(0.3) # to capture the alert
                    confiot.device_screenshot(count)
        count += 1
    # TouchEvent(state=8f9faca9459fa27a8a33eb1a9da4cc07, view=e26dde88a959dcc2ab4d2f04eb1fb85a(PluginRNActivityCamera}/ImageView-))
    # TouchEvent(state=8f9faca9459fa27a8a33eb1a9da4cc07, view=e26dde88a959dcc2ab4d2f04eb1fb85a(PluginRNActivityCamera}/ImageView-))


if __name__ == "__main__":
    # test_goto_state()
    test_do_event()

    # path = confiot.utg_graph.find_shortest_path(confiot.utg_graph.start_node, "64f90b2eddcdefb5f3f4c902ebcba04e")

    # event_path = []
    # if (path):
    #     current_node = path[0]
    #     for node in path[1:]:
    #         event_path.append(confiot.utg_graph.edges_dict[current_node.name][node.name][0])
    #         current_node = node
    # print(event_path)
