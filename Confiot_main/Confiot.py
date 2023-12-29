###############################################
# Confiot.py
# This class is the entrance of analyzing the app policies
###############################################
import json
import os
import sys
import copy
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + "/../")

from droidbot_origin.droidbot.input_event import *
from droidbot_origin.droidbot.device import Device
from droidbot_origin.droidbot.app import App
from droidbot_origin.droidbot.device_state import DeviceState
from Confiot_main.util import deprecated, DirectedGraph, Node, Edge, draw_rect_with_bounds, png_resize, UITree, query_config_resource_mapping, parse_config_resource_mapping
import Confiot_main.settings as settings
from Confiot_main.UIComparator import UIComparator

DONE = '''
###################
###    Done   #####
###################
'''


class ConfiotGuest:

    def __init__(self) -> None:
        self.device: Device = None
        self.app: App = None
        self.utg_graph: DirectedGraph = None
        self.uiTree: UITree = None
        self.ConfigResourceMapper = []

        # {"event_str": event_json_path}
        self.events_fpath = {}
        # {"event_str": event_dict}
        self.events = {}
        # {"state_str": [view,]}
        self.state_contents = {}
        self.conf_list = []
        '''
        # the result that indicates the influence of the config `host_analyzing_config`
        {
            "id":0,
            "influenceType": CONFIG_DISABLED,
            "content" : {}
        }
        '''
        self.result = []

        print("Analyzing the app: ", settings.app_path)
        print("Device serial: ", settings.device_serial)
        print("Output path: ", settings.droid_output)

        self.parse_event()
        self.parse_utg()
        self.parse_state_json()
        self.parse_conf_list()

    def device_connect(self):
        self.device = Device(device_serial=settings.device_serial, ignore_ad=True, output_dir=settings.Confiot_output)
        self.app = App(app_path=settings.app_path, output_dir=settings.Confiot_output)
        self.device.connect()
        self.device.install_app(self.app)

    # parse the description configurations
    @deprecated
    def device_get_all_description_config(self):
        STEP0 = '''
######################################################################
###    Traverse static UI states for configurations extraction   #####
######################################################################
'''
        print(STEP1)
        for node in self.utg_graph.nodes:
            finished = self.device_to_state(host_analyzing_config, node.name)
            if (finished):
                self.device_get_UIElement(host_analyzing_config, node.name)

    # get all configurations list and test them one by one
    def device_guest_config_walker(self, host_analyzing_config: str):
        # test all configs in conf_list and genreate UI hierachy and screenshots
        STEP2 = '''
###################################
### Testing guest configs #########
###################################
'''
        print(STEP2)
        for conf in self.conf_list:
            enabled = self.device_guest_config_test(host_analyzing_config, conf)
            if (not enabled):
                infl = {}
                infl["id"] = len(self.conf_list)
                infl["influenceType"] = settings.CONFIG_DISABLED
                infl["content"] = {}
                infl["content"]["view"] = conf["view_images"]
                infl["content"]["state"] = conf["from_state"]
                self.result.append(infl)

    # analyze the state transition screenshots of the configs in conf_list with gpt
    def device_guest_config_GPTAnalyze(self, host_analyzing_config: str):
        STEP3 = '''
###################################
### Testing guest configs with GPT#
###################################
'''
        print(STEP3)
        for conf in self.conf_list:
            out_dir = settings.UI_output + f"/{host_analyzing_config}/guest:" + conf["view_images"]
            if (os.path.exists(out_dir + "/before.png") and os.path.exists(out_dir + "/after.png")):
                time.sleep(1)
                ret = UIComparator.identify_alert(out_dir + "/before.png", out_dir + "/after.png")
                if (ret == "fail"):
                    infl = {}
                    infl["id"] = len(self.conf_list)
                    infl["influenceType"] = settings.CONFIG_DISABLED
                    infl["content"] = {}
                    infl["content"]["view"] = conf["view_images"]
                    infl["content"]["state"] = conf["from_state"]
                    self.result.append(infl)

    def device_connect(self):
        self.device = Device(device_serial=settings.device_serial, ignore_ad=True)
        self.app = App(app_path=settings.app_path, output_dir=settings.Confiot_output)
        #self.device.connect()
        self.device.install_app(self.app)

        print(DONE)

    def device_map_config_resource(self):
        STEP0 = '''
######################################################################
#############    Configuration-Resources Mapping   ###################
######################################################################
'''
        print(STEP0)

        paths = self.parse_UITree()
        paths_str = ""

        for p in paths:
            p_str = "\",\"".join(p)
            paths_str += f"[\"{p_str}\"]\n"

        prompt = ''
        with open(BASE_DIR + "/prompt/ConfigResourceMapping.txt") as f:
            prompt = f.read()

        prompt = prompt.replace("{{PATHLIST}}", paths_str)
        print(prompt)
        print(
            "----------------------------------------------------------------------------------------------------------------------------------------------"
        )
        # os.environ["https_proxy"] = "http://192.168.72.1:1083"
        res = query_config_resource_mapping(prompt)

        if (res):
            with open(BASE_DIR + "/prompt/response.txt", "w") as f:
                f.write(res)
            self.ConfigResourceMapper = parse_config_resource_mapping(res)

        print(DONE)
        return self.ConfigResourceMapper

    def device_get_UIElement(self, host_analyzing_config: str, current_state_str: str, store_path="", store_file=""):
        output_path = ''
        output_file = ''
        if (store_file == ''):
            output_path = settings.UI_output + f"/{host_analyzing_config}/"
            output_file = output_path + f"{current_state_str}.xml"
        else:
            output_path = store_path
            output_file = store_path + "/" + store_file
        if (not os.path.exists(output_path)):
            os.makedirs(output_path)

        try:
            ui_dump = output_file.replace('/', '_')
            if (self.device and self.app):
                r1 = self.device.adb.shell(f"uiautomator dump /sdcard/{ui_dump}")
                r2 = self.device.adb.run_cmd(["pull", f"/sdcard/{ui_dump}", output_file])
        # failed to dump the UI Hierarchy with adb
        except:
            print("[DBG]: Failed to dump the UI Hierarchy with adb and try to dump with Accessibility!")
            try:
                if (self.device.connected):
                    import xml.etree.ElementTree as ET
                    views = self.device.get_views()
                    root = ET.Element('Hierarchy')

                    for item in views:
                        entry = ET.SubElement(root, 'Node')
                        for key, value in item.items():
                            ET.SubElement(entry, key).text = str(value)
                    tree = ET.ElementTree(root)
                    tree.write(output_file)
                else:
                    print("[ERR]: Device not connected!")
            except Exception as e:
                print("[ERR]: Failed to dump the UI Hierachy!", e)

    def device_screenshot(self, store_dir: str):
        local_image_path = store_dir
        remote_image_path = "/sdcard/screen.png"
        self.device.adb.shell("screencap -p %s" % remote_image_path)
        self.device.pull_file(remote_image_path, local_image_path)
        self.device.adb.shell("rm %s" % remote_image_path)

    def device_stop_app(self, autodroid=False):
        from AutoDroid.droidbot.input_event import IntentEvent as autoIntentEvent
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
            go_back_event = autoIntentEvent(stop_app_intent) if autodroid else IntentEvent(stop_app_intent)
            go_back_event.send(self.device)
        except Exception as e:
            print("[ERR]: Cannot stop app caused by: ", e)

    def device_to_state(self, host_analyzing_config: str, target_state: str):
        event_str_path = []
        path = self.utg_graph.find_shortest_path(self.utg_graph.start_node, target_state)
        if (path):
            current_node = path[0]
            for node in path[1:]:
                event_str_path.append(self.utg_graph.edges_dict[current_node.name][node.name][0])
                current_node = node

        self.device_stop_app()
        self.device.start_app(self.app)
        time.sleep(5)
        for estr in event_str_path:
            if (estr in self.events_fpath):
                event_dict = self.events[estr]
                event = InputEvent.from_dict(event_dict)
                print("[DBG]: Action: " + estr)
                event.send(self.device)
                time.sleep(2)
            else:
                print("[ERR]: Wrong event path: ", event_str_path)
                return False

        print("[DBG]: Reached state: " + target_state)
        return True

    def TOSTATE(self, target_state, app, device):
        self.app = app
        self.device = device

        self.parse_event()
        # print(confiot.events)
        self.parse_utg()

        event_str_path = []
        path = self.utg_graph.find_shortest_path(self.utg_graph.start_node, target_state)
        if (path):
            current_node = path[0]
            for node in path[1:]:
                event_str_path.append(self.utg_graph.edges_dict[current_node.name][node.name][0])
                current_node = node

        # self.device_stop_app(autodroid=True)
        # self.device.start_app(self.app)
        # time.sleep(3)

        ret_events = []
        for estr in event_str_path:
            if (estr in self.events_fpath):
                event_dict = self.events[estr]
                event = InputEvent.from_dict(event_dict)
                print("[DBG]: Action: " + estr)
                ret_events.append(event)
                # event.send(self.device)
                # time.sleep(2)
            else:
                print("[ERR]: Wrong event path: ", event_str_path)
                return False

        print("[DBG]: Reached state: " + target_state)
        return ret_events

    # return True if the config is enabled
    # return False if the config is possiblly be disabled
    def device_guest_config_test(self, host_analyzing_config: str, guest_config):
        conf_activity_dict = guest_config
        target_state = conf_activity_dict["from_state"]
        config_view_name = guest_config["view_images"]
        config_event = conf_activity_dict["event"]
        config_bounds = conf_activity_dict["bounds"]
        config_bounds = f"[{config_bounds[0][0]},{config_bounds[0][1]}][{config_bounds[1][0]},{config_bounds[1][1]}]"

        print("[DBG]: {host}: " + host_analyzing_config + "{guest}: " + config_view_name)

        if (config_view_name == ''):
            print("[ERR]: Cannot find view image")
            return None

        finished = self.device_to_state(host_analyzing_config, target_state)
        out_dir = settings.UI_output + f"/{host_analyzing_config}/guest:" + config_view_name
        if (finished):
            if (config_event is not None):
                self.device_get_UIElement(host_analyzing_config, target_state, out_dir, "/before.xml")
                self.device_screenshot(out_dir + "/before.png")
                draw_rect_with_bounds(out_dir + "/before.png", conf_activity_dict["bounds"])
                time.sleep(1)
                config_event.send(self.device)
                time.sleep(3)
                self.device_get_UIElement(host_analyzing_config, target_state, out_dir, "/after.xml")
                self.device_screenshot(out_dir + "/after.png")
        else:
            print("[ERR]: Failed to goto target state to test config :", guest_config)
            return None

        if (os.path.exists(out_dir + "/before.xml") and os.path.exists(out_dir + "/after.xml")):
            return UIComparator.compare_xml_files_with_bounds(out_dir + "/before.xml", out_dir + "/after.xml", config_bounds)
        else:
            print("[ERR]: Failed to generate UI hierachy for: ", guest_config)
            return None

    ###############################################################
    ###############################################################
    def parse_event(self):
        events_path = settings.droid_output + "/events/"
        events_json = os.listdir(events_path)
        for j in events_json:
            with open(events_path + j, "r") as f:
                try:
                    event = json.load(f)
                    event_str = event["event_str"]
                    if (event_str != ''):
                        self.events_fpath[event_str] = events_path + j
                        self.events[event_str] = event["event"]
                except Exception as e:
                    print(f"[ERR]: Failed to parse the event file `{j}`\n" + str(e))

    def parse_utg(self) -> DirectedGraph:
        self.utg_graph = DirectedGraph()
        utg_nodes = {}

        utg_dict = {}
        utg_nodes_dict = []
        utg_edges_dict = []

        with open(settings.droid_output + "/utg.js", "r") as f:
            utg_content = f.read()
            if (utg_content != ''):
                utg_content = utg_content.replace("var utg = ", '')
                utg_content = utg_content.replace(";", "")
                utg_dict = json.loads(utg_content)
                utg_nodes_dict = utg_dict["nodes"]
                utg_edges_dict = utg_dict["edges"]

                for node in utg_nodes_dict:
                    activity = (node["package"] + node["activity"]).replace("}", "")
                    if (activity == utg_dict["app_main_activity"]):
                        self.utg_graph.start_node = node["state_str"]
                        break

        if (utg_nodes_dict != [] and utg_edges_dict != [] and self.utg_graph.start_node is not None):
            print("Start state: " + self.utg_graph.start_node)
        else:
            print("[ERR]: Cannot find start state")
            return None

        # parse utg with DirectedGraph
        for n in utg_nodes_dict:
            self.utg_graph.add_node(Node(n["state_str"]))
            utg_nodes[n["state_str"]] = self.utg_graph.nodes[-1]

        for e in utg_edges_dict:
            event_strs = [eve["event_str"] for eve in e["events"]]
            self.utg_graph.add_edge(Edge(utg_nodes[e["from"]], utg_nodes[e["to"]], event_strs))

        self.utg_graph.utg_nodes = utg_nodes_dict
        self.utg_graph.utg_edges = utg_edges_dict

        return self.utg_graph

    # parse all UI hierachy in state
    def parse_state_json(self):
        states_path = f"{settings.droid_output}/states/"
        states_json = os.listdir(states_path)
        for j in states_json:
            if ("screen" in j):
                continue
            with open(states_path + j, "r") as f:
                try:
                    s = json.load(f)
                    state_str = s["state_str"]
                    if (state_str != ''):
                        self.state_contents[state_str] = s["views"]
                except Exception as e:
                    print(f"[ERR]: Failed to parse the state file `{j}`\n" + str(e))

    # 获取与config_id配置相关的文本描述（child/brother node）
    def get_related_descrition(self, state, config_id):
        config_description = ""

        if (state not in self.state_contents):
            return -1
        if (config_id >= len(self.state_contents[state])):
            return -1
        current_config = self.state_contents[state][config_id]
        child_configs = current_config['children']

        if ("content_description" in current_config and current_config["content_description"] and
                current_config["content_description"] != ''):
            config_description = config_description + f"{current_config['content_description']}"
        if ("text" in current_config and current_config["text"] and current_config["text"] != ''):
            config_description = config_description + f";{current_config['text']}"

        for ch in child_configs:
            desc = self.get_related_descrition(state, ch)
            if (desc != -1 and desc != ''):
                config_description = config_description + desc

        return config_description

    # 返回所有config paths
    def parse_UITree(self):
        self.uiTree = UITree()

        # {state_str: [Node,]} 存储当前state下所有config Node
        config_nodes = {}
        # {event_str: Node} event与config一一对应
        event_config = {}

        if (self.utg_graph is None):
            return

        # for e in self.events:
        #     if(hasattr(e, 'view')):
        #         config_id = str(e['view']['temp_id'])
        #         config_description = ''

        #         if(hasattr(e['view'], "content_description") and e['view']["content_description"] and e['view']["content_description"] != ''):
        #             config_description = config_description + ";e['view']['content_description']"
        #         if(hasattr(e['view'], "text") and e['view']["text"] and e['view']["text"] != ''):
        #             config_description = config_description + ";e['view']['text']"
        #         self.uiTree.add_node(Node(config_id,description=config_description))

        # 获取每个state中存在的config Node
        for src_state in self.utg_graph.edges_dict:
            for target_state in self.utg_graph.edges_dict[src_state]:
                for event_str in self.utg_graph.edges_dict[src_state][target_state]:
                    e = self.events[event_str]

                    # 不包括返回的边
                    if ("name=BACK" in event_str):
                        continue

                    if ('view' in e):
                        config_id = str(e['view']['temp_id'])
                        config_description = self.get_related_descrition(src_state, int(config_id))

                        if (src_state not in config_nodes):
                            config_nodes[src_state] = []
                        n = Node(config_id, description=config_description, state=src_state)
                        event_config[event_str] = n
                        config_nodes[src_state].append(n)
                        self.uiTree.add_node(n)

        indegree = {}
        for n in self.uiTree.nodes:
            indegree[n] = 0
        for utg_edge in self.utg_graph.utg_edges:
            if utg_edge['to'] not in config_nodes:
                continue
            for config in config_nodes[utg_edge['to']]:
                if (utg_edge['events'] == []):
                    continue
                event_str = utg_edge['events'][0]['event_str']
                if event_str not in event_config:
                    continue
                e = Edge(event_config[event_str], config, event_str)
                indegree[config] += 1
                self.uiTree.add_edge(e)

        start_node = list(indegree.keys())[0]
        for n in indegree:
            if (indegree[n] < indegree[start_node]):
                start_node = n

        self.uiTree.start_node = start_node.name

        print("[DBG]: UITree start node:", start_node)
        UITree.draw(self.uiTree, settings.Confiot_output)

        config_paths = []
        for n in self.uiTree.nodes:
            p = self.uiTree.find_shortest_path(self.uiTree.start_node, n.name)
            p = [i.description for i in p]
            config_paths.append(p)

        return config_paths

    def parse_conf_list(self):
        # input: droid_output/utg.js -> edges
        # output: conf_activity_dict (view_images, {event_id, event_str, {from_state, to_state}}, activity)
        utg_edges_dict = self.utg_graph.utg_edges
        conf_list = []
        # {'from': '6578c97fcb7eb008507ccde68f80d360', 'to': 'ddd93f40628f40c0b4105d3cc0f69a26', 'id': '6578c97fcb7eb008507ccde68f80d360-->ddd93f40628f40c0b4105d3cc0f69a26', 'title': '<table class="table">\n<tr><th>1166</th><td>TouchEvent(state=6578c97fcb7eb008507ccde68f80d360, view=bba1713c7fb66a73d605cc227313a1cf(CustomTabActivity}/View-))</td></tr>\n</table>', 'label': '1166', 'events': [{'event_str': 'TouchEvent(state=6578c97fcb7eb008507ccde68f80d360, view=bba1713c7fb66a73d605cc227313a1cf(CustomTabActivity}/View-))', 'event_id': 1166, 'event_type': 'touch', 'view_images': ['views/view_bba1713c7fb66a73d605cc227313a1cf.png']}]}
        # print(edges_dict)
        cid = 0
        for e in utg_edges_dict:
            conf_activity_dict = {}
            if (e["events"] == []):
                continue

            c = {}
            for conf in conf_list:
                if (e["events"][0]["view_images"] == conf["view_images"]):
                    c = conf
                    break
            if c != {}:
                continue

            if (e["events"][0]["view_images"] != []):
                conf_activity_dict["view_images"] = e["events"][0]["view_images"][0].replace("views/", "")
            else:
                conf_activity_dict["view_images"] = ""
            conf_activity_dict["event_id"] = e["events"][0]["event_id"]
            conf_activity_dict["event_str"] = e["events"][0]["event_str"]
            conf_activity_dict["from_state"] = e["from"]
            conf_activity_dict["to_state"] = e["to"]

            # Add bounds and InputEvent for views identification
            conf_activity_dict["event"] = None
            conf_activity_dict["bounds"] = None
            if (conf_activity_dict["event_str"] in self.events_fpath):
                event_dict = self.events[conf_activity_dict["event_str"]]
                event = InputEvent.from_dict(event_dict)
                conf_activity_dict["event"] = event
                if ("view" in event_dict):
                    conf_activity_dict["bounds"] = event_dict["view"]["bounds"]

            if (conf_activity_dict["bounds"] is None):
                # print("[ERR]: Cannot find view bounds for event: ", conf_activity_dict["event_str"])
                continue

            if (e["events"][0]["event_str"].split("(")[0] == "KeyEvent"):
                conf_activity_dict["activity"] = conf_list[-1]["activity"]
            elif (len(e["events"][0]["event_str"].split("(")) < 3):
                # IntentEvent: start and stop, skip
                conf_activity_dict["activity"] = ''
                continue
            else:
                conf_activity_dict["activity"] = e["events"][0]["event_str"].split("(")[2].split("}/")[0]

            if (conf_activity_dict["activity"] == "ChooseDeviceActivity" or
                    conf_activity_dict["activity"] == "ScanBarcodeActivity" or
                    conf_activity_dict["activity"] == "ChooseSubCategoryDeviceActivity" or
                    conf_activity_dict["activity"] == "WebShellActivity" or conf_activity_dict["activity"] == "MainActivity" or
                    conf_activity_dict["activity"] == "ResolverActivity" or
                    conf_activity_dict["activity"] == "HomeAllStyleListActivity" or
                    conf_activity_dict["activity"] == "HomeStyleActivity" or
                    conf_activity_dict["activity"] == "HomeRoomBackgroundPreviewActivity" or
                    conf_activity_dict["activity"] == "HomeRoomBackgroundActivity" or
                    conf_activity_dict["activity"] == "ImagePreviewActivity" or
                    conf_activity_dict["activity"] == "LoginH5HomeAcvtivity" or
                    conf_activity_dict["activity"] == "CustomTabActivity"):
                continue

            conf_activity_dict["cid"] = cid
            cid += 1
            conf_list.append(conf_activity_dict)

        self.conf_list = conf_list
        conf_list_printable = copy.deepcopy(conf_list)
        for c in conf_list_printable:
            c["event"] = None

        json_str = json.dumps(conf_list_printable)
        with open(settings.Confiot_output + "/guest_config_list.json", "w") as f:
            f.write(json_str)
        #print(conf_list)

    def _scroll_to_top(self, scroller, all_views_for_mark, old_state=None):
        prefix_scroll_event = []
        if old_state is None:
            old_state = self.device.get_current_state()
        for _ in range(3):  # first scroll up to the top
            self.device.send_event(ScrollEvent(view=scroller, direction="UP"))
            scrolled_state = self.device.get_current_state()
            old_state = scrolled_state
            state_prompt, scrolled_candidate_actions, scrolled_views, _ = scrolled_state.get_described_actions()
            scrolled_new_views = []  # judge whether there is a new view after scrolling
            for scrolled_view in scrolled_views:
                if scrolled_view not in all_views_for_mark:
                    scrolled_new_views.append(scrolled_view)
                    all_views_for_mark.append(scrolled_view)
            if len(scrolled_new_views) == 0:
                break

            prefix_scroll_event.append(ScrollEvent(view=scroller, direction="UP"))
        return prefix_scroll_event

    def parse_all_views(self, current_state: DeviceState):
        scrollable_views = current_state.get_scrollable_views()  #self._get_scrollable_views(current_state)

        if len(scrollable_views) > 0:
            '''
            if there is at least one scroller in the screen, we scroll each scroller many times until all the screens after scrolling have been recorded, you do not need to read
            '''
            # print(scrollable_views)

            actions_dict = {}
            whole_state_views, whole_state_actions, whole_state_strs = [], [], []

            # state_strs = [current_state.state_str]
            state_prompt, current_candidate_actions, current_views, _ = current_state.get_described_actions()
            all_views_for_mark = copy.deepcopy(
                current_views)  # just for judging whether the screen has been scrolled up to the top

            for scrollerid in range(len(scrollable_views)):
                scroller = scrollable_views[scrollerid]
                # prefix_scroll_event = []
                actions_dict[scrollerid] = []

                prefix_scroll_event = self._scroll_to_top(scroller, all_views_for_mark)

                # after scrolling to the top, update the current_state
                top_state = self.device.get_current_state()
                state_prompt, top_candidate_actions, top_views, _ = top_state.get_described_actions()
                all_views_without_id, all_actions = top_views, top_candidate_actions

                too_few_item_time = 0

                for _ in range(3):  # then scroll down to the bottom
                    whole_state_strs.append(top_state.state_str)  # record the states from the top to the bottom
                    self.device.send_event(ScrollEvent(view=scroller, direction="DOWN"))
                    scrolled_state = self.device.get_current_state()
                    state_prompt, scrolled_candidate_actions, scrolled_views, _ = scrolled_state.get_described_actions()

                    scrolled_new_views = []
                    for scrolled_view_id in range(len(scrolled_views)):
                        scrolled_view = scrolled_views[scrolled_view_id]
                        if scrolled_view not in all_views_without_id:
                            scrolled_new_views.append(scrolled_view)
                            all_views_without_id.append(scrolled_view)
                            all_actions.append(
                                prefix_scroll_event +
                                [ScrollEvent(view=scroller, direction="DOWN"), scrolled_candidate_actions[scrolled_view_id]])
                    # print('found new views:', scrolled_new_views)
                    if len(scrolled_new_views) == 0:
                        break

                    prefix_scroll_event.append(ScrollEvent(view=scroller, direction="DOWN"))

                    if len(scrolled_new_views) < 2:
                        too_few_item_time += 1
                    if too_few_item_time >= 2:
                        break

                    # self.utg.add_transition(ScrollEvent(view=scroller, direction="DOWN"), top_state, scrolled_state)
                    top_state = scrolled_state

                # filter out the views that have been added to the whole_state by scrolling other scrollers
                for all_view_id in range(len(all_views_without_id)):
                    view = all_views_without_id[all_view_id]
                    if view not in whole_state_views:
                        whole_state_views.append(view)
                        whole_state_actions.append(all_actions[all_view_id])

                all_views_for_mark = []
                _ = self._scroll_to_top(scroller, all_views_for_mark, top_state)
        else:
            whole_state_views, whole_state_actions, whole_state_strs = [], [], []

            # state_strs = [current_state.state_str]
            state_prompt, current_candidate_actions, current_views, _ = current_state.get_described_actions()
            for all_view_id in range(len(current_views)):
                view = current_views[all_view_id]
                if view not in whole_state_views:
                    whole_state_views.append(view)

        return whole_state_views


class ConfiotHost(Confiot):

    # [TODO]: update
    def test_vistor_mode(self, config_description_list):
        for desc in config_description_list:
            state = desc["state"]
            configs = desc["configs"]
            for config in configs:
                text = config["description"].encode().decode()
                if ("vistor mode" in text.lower() or "访客模式" in text.lower()):
                    return state
        return None

    def generate_tasks(self):
        config_description_list = []
        with open(settings.Confiot_output + "/config_description_list.json", "r") as f:
            config_description_list = json.loads(f.read())

        target_state = self.test_vistor_mode(config_description_list)
        if (target_state is not None):
            self.device_to_state('', target_state)

    def start_autodroid(self):
        command = f"autodroid -d 192.168.31.218:5555 -a /root/documents/droidbot-new/mihome/mihome.apk -o /root/documents/droidbot-new/mihome/mihome-smartscale/result/autodroid -task 'Configure the device Mihome body fat scale for enabling the guest mode' -keep_env -keep_app"

        # 使用subprocess.Popen执行命令，并捕获标准输出
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        # 逐行读取标准输出
        while True:
            line = process.stdout.readline()
            if not line:
                break  # 如果没有更多的输出，则退出循环
            print(line.strip())
            process.stdout.flush()  # 刷新输出缓冲区

        # 等待子进程结束
        process.wait()


class ConfiotGuest(Confiot):
    # walk through all states and store the UI hierachy in UI/
    def device_state_walker(self, host_analyzing_config: str):
        STEP1 = '''
###################################
### Traverse static UI states #####
###################################
'''
        print(STEP1)
        for node in self.utg_graph.nodes:
            finished = self.device_to_state(host_analyzing_config, node.name)
            if (finished):
                self.device_get_UIElement(host_analyzing_config, node.name)

        print(DONE)

    # get all configurations list and test them one by one
    def device_guest_config_walker(self, host_analyzing_config: str):
        # test all configs in conf_list and genreate UI hierachy and screenshots
        STEP2 = '''
###################################
### Testing guest configs #########
###################################
'''
        print(STEP2)
        for conf in self.conf_list:
            enabled = self.device_guest_config_test(host_analyzing_config, conf)
            if (not enabled):
                infl = {}
                infl["id"] = len(self.conf_list)
                infl["influenceType"] = settings.CONFIG_DISABLED
                infl["content"] = {}
                infl["content"]["view"] = conf["view_images"]
                infl["content"]["state"] = conf["from_state"]
                self.result.append(infl)

    # analyze the state transition screenshots of the configs in conf_list with gpt
    def device_guest_config_GPTAnalyze(self, host_analyzing_config: str):
        STEP3 = '''
###################################
### Testing guest configs with GPT#
###################################
'''
        print(STEP3)
        for conf in self.conf_list:
            out_dir = settings.UI_output + f"/{host_analyzing_config}/guest:" + conf["view_images"]
            if (os.path.exists(out_dir + "/before.png") and os.path.exists(out_dir + "/after.png")):
                time.sleep(1)
                # resize the images
                before_png_resize = png_resize(out_dir + "/before.png", settings.resol_x, settings.resol_y)
                after_png_resize = png_resize(out_dir + "/after.png", settings.resol_x, settings.resol_y)
                if (before_png_resize != -1 and after_png_resize != -1 and os.path.exists(before_png_resize) and
                        os.path.exists(after_png_resize)):
                    ret = UIComparator.identify_alert(before_png_resize, after_png_resize, out_dir)
                    if (ret == "fail"):
                        infl = {}
                        infl["id"] = len(self.conf_list)
                        infl["influenceType"] = settings.CONFIG_DISABLED
                        infl["content"] = {}
                        infl["content"]["view"] = conf["view_images"]
                        infl["content"]["state"] = conf["from_state"]
                        self.result.append(infl)
