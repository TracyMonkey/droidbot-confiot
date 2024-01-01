import os, sys
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + "/../")
from Confiot_main.Confiot import ConfiotGuest, ConfiotHost, Confiot
import xml.etree.ElementTree as ET
from Confiot_main.UIComparator import UIComparator
import os

# For test
HOST_CONFIG_ANALYZED = "host:mihome_After_SHARE"


def test_resize_png():
    from Confiot_main.util import png_resize
    png_resize(
        "/root/documents/droidbot-new/a2dp/Confiot/UI/host:A2DP_Start_at_Boot_off/guest:view_0fe88b3189e686f7242ae495c9b79a4a.png/after.png",
        230, 512)


#####################################


def test_goto_state():
    confiot = ConfiotGuest()
    confiot.device_connect()

    # print(confiot.events)

    while (1):
        target_str = input("state: ")
        if (target_str == '\n' or target_str == ''):
            confiot.device_stop_app()
            break
        confiot.device_to_state(HOST_CONFIG_ANALYZED, target_str)


def test_stop_app():
    confiot = ConfiotGuest()
    confiot.device_connect()

    confiot.device_stop_app()


def test_state_walker():
    confiot = ConfiotGuest()
    confiot.device_connect()

    # print(confiot.events)

    confiot.device_state_walker("A2DP_Start_at_Boot_off")


def test_config_extract():
    confiot = ConfiotGuest()
    #confiot.device_connect()

    # print(confiot.events)


def test_guest_config_dynamic_analyze():
    confiot = ConfiotGuest()
    confiot.device_connect()

    confiot.parse_event()
    # print(confiot.events)
    confiot.parse_utg()
    confiot.parse_conf_list()

    print(confiot.conf_list[44])
    print(confiot.device_guest_config_test(HOST_CONFIG_ANALYZED, confiot.conf_list[44]))


def test_xml_parse():
    out_dir = "/root/documents/droidbot-new/a2dp/Confiot/UI/host:A2DP_Start_at_Boot_off/view_80907fa95fc546d10b3034979424ff23.png"
    config_bounds = "[965,129][1080,267]"

    before_xml = ET.parse(out_dir + "/before.xml")
    after_xml = ET.parse(out_dir + "/after.xml")

    before_root = before_xml.getroot()
    after_root = after_xml.getroot()

    print("[DBG]: Find config in bounds: ", config_bounds)
    before_config_node = before_root.findall(f".//*[@bounds='{config_bounds}']")
    after_config_node = after_root.findall(f".//*[@bounds='{config_bounds}']")

    # 打印相关的node元素
    for node in before_config_node:
        print(ET.tostring(node, encoding='unicode'))

    for node in after_config_node:
        print(ET.tostring(node, encoding='unicode'))


def test_identify_alert():
    os.environ["https_proxy"] = "http://192.168.72.1:1083"
    before_image_path = "/root/documents/droidbot-new/a2dp/Confiot/UI/host:A2DP_Start_at_Boot_off/guest:view_80907fa95fc546d10b3034979424ff23.png/before.png"
    after_image_path_test1 = "/root/documents/droidbot-new/a2dp/Confiot/UI/host:A2DP_Start_at_Boot_off/guest:view_80907fa95fc546d10b3034979424ff23.png/after.png"
    # image_path_no_alert_test = "/Users/tracy/Documents/GitHub/droidbot/mihome/pixel5/states/screen_2023-11-20_174510.png"
    print(UIComparator.identify_alert(before_image_path, before_image_path))


def test_device_guest_config_walker():
    os.environ["https_proxy"] = "http://192.168.72.1:1083"

    confiot = ConfiotGuest()
    confiot.device_connect()

    # print(confiot.events)

    confiot.device_state_walker(HOST_CONFIG_ANALYZED)
    confiot.device_guest_config_walker(HOST_CONFIG_ANALYZED)
    confiot.device_guest_config_GPTAnalyze(HOST_CONFIG_ANALYZED)

    print(confiot.result)


def test_STEP0():
    confiot = ConfiotGuest()
    confiot.device_connect()

    # print(confiot.events)

    confiot.device_get_all_description_config()


def test_STEP1():
    confiot = ConfiotGuest()
    confiot.device_connect()

    # print(confiot.events)

    confiot.device_state_walker(HOST_CONFIG_ANALYZED)


def test_host():
    import Confiot_main.settings as settings
    settings.device_serial = "192.168.31.218:5555"
    confiot = ConfiotHost()
    confiot.device_connect()

    # print(confiot.events)

    #confiot.generate_tasks()
    confiot.start_autodroid()


def test_get_ui_hierarchy():
    import Confiot_main.settings as settings
    import json
    settings.device_serial = "192.168.31.218:5555"
    confiot = ConfiotHost()
    confiot.device_connect()
    while (input() != '1'):
        confiot.device_get_UIElement("", "", "/root/documents/droidbot-confiot/Confiot_main/", "output.json")

    # while(input() != '1'):
    #     a= confiot.device.get_views()
    #     json_data = json.dumps(a, indent=2)  # indent 参数用于设置缩进，使 JSON 文件更易读

    #     # 将 JSON 数据写入文件
    #     with open('output.json', 'w') as json_file:
    #         json_file.write(json_data)


def test_mapping_uitree():
    import Confiot_main.settings as settings
    from Confiot_main.util import query_config_resource_mapping, parse_config_resource_mapping
    # settings.device_serial = "192.168.31.218:5555"
    # settings.app_path = "/root/documents/droidbot-new/a2dp/a2dp.Vol_169.apk"
    # settings.droid_output = "/root/documents/droidbot-new/a2dp/"

    confiot = Confiot()
    #confiot.device_connect()

    # print(confiot.events)

    paths = confiot.device_map_config_resource()








if __name__ == "__main__":
    #test_device_guest_config_walker()
    # test_resize_png()
    # test_STEP0()
    test_mapping_uitree()
