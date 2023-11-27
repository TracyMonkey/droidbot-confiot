###############################################
# Confiot.py
# This class is the entrance of analyzing the app policies
###############################################
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + "/../")

from droidbot.input_event import *
from droidbot.device import Device
from droidbot.app import App
from Confiot.util import DirectedGraph, Node, Edge
import Confiot.settings


class Confiot:

    def __init__(self) -> None:
        self.device: Device = None
        self.app: App = None
        self.utg_graph: DirectedGraph = None
        # {"event_str": event_json_path}
        self.events = {}

    def device_connect(self):
        self.device = Device(device_serial=settings.device_serial, ignore_ad=True)
        self.app = App(app_path=settings.app_path, output_dir=settings.Confiot_output)
        #self.device.connect()
        self.device.install_app(self.app)

    def device_get_UIElement(self, analyzing_progress: str, current_state_str: str):
        output_path = settings.UI_output + f"/{analyzing_progress}/"
        if (self.device and self.app):
            self.device.adb.shell("uiautomator dump /sdcard/ui_dump.xml")
            if (not os.path.exists(output_path)):
                os.makedirs(output_path)
            self.device.adb.run_cmd(["pull", "/sdcard/ui_dump.xml", output_path + f"{current_state_str}.xml"])

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

    def device_to_state(self, analyzing_progress: str, target_state: str):
        event_str_path = []
        path = self.utg_graph.find_shortest_path(self.utg_graph.start_node, target_state)
        if (path):
            current_node = path[0]
            for node in path[1:]:
                event_str_path.append(self.utg_graph.edges_dict[current_node.name][node.name][0])
                current_node = node

        self.device_stop_app()
        self.device.start_app(self.app)
        for estr in event_str_path:
            if (estr in self.events):
                with open(self.events[estr], "r") as f:
                    event_dict = json.load(f)["event"]
                    event = InputEvent.from_dict(event_dict)
                    print("[DBG]: Action: " + estr)
                    event.send(self.device)
            else:
                print("[ERR]: Wrong event path: ", event_str_path)
                break

        self.device_get_UIElement(analyzing_progress, target_state)
        print("[DBG]: Finish state: " + target_state + "\n")

    def device_state_walker(self, analyzing_progress: str):
        for node in self.utg_graph.nodes:
            self.device_to_state(analyzing_progress, node.name)

    def parse_event(self):
        events_path = settings.droid_output + "/events/"
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

        with open(settings.droid_output + "/utg.js", "r") as f:
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

    # path = confiot.utg_graph.find_shortest_path(confiot.utg_graph.start_node, "64f90b2eddcdefb5f3f4c902ebcba04e")

    # event_path = []
    # if (path):
    #     current_node = path[0]
    #     for node in path[1:]:
    #         event_path.append(confiot.utg_graph.edges_dict[current_node.name][node.name][0])
    #         current_node = node
    # print(event_path)
