import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + "/../")

from Confiot_main.settings import settings
from Confiot_main.util import deprecated
from Confiot_main.UIComparator import UIComparator

import re


class PolicyGenerator:

    # 通过分析STEP1:device_state_replay的输出结果，生成policy
    def Policy_generate_1(self, host_analyzing_config_before, host_analyzing_config_after, state_str, ConfigResourceMapper):
        add_related_resources = set()
        remove_related_resources = set()
        potential_policies = []

        comparator = UIComparator(host_analyzing_config_before, host_analyzing_config_after)

        hierachy_compare_result = comparator.compare_output_path + f"{state_str}.html"
        UI_add = comparator.get_UI_add(hierachy_compare_result)
        UI_delete = comparator.get_UI_delete(hierachy_compare_result)

        # print(UI_add, UI_delete)

        for node in UI_add:
            text = re.findall("text=\"(.*?)\"", node["element"])
            if (text):
                text = text[0].strip()
            else:
                text = ""
            content = re.findall("content-desc=\"(.*?)\"", node["element"])
            if (content):
                content = content[0].strip()
            else:
                content = ""

            if (text == '' and content == ''):
                continue

            desc = text + content
            desc = re.findall("[a-zA-Z]+", desc)
            # 希望是完整的单词
            if (len(desc) > 0 and len(desc[0]) > 2):
                for cr in ConfigResourceMapper:
                    if (state_str != cr["state"]):
                        continue

                    if (text != '' and text in cr["Path"][-1]):
                        for r in cr["Resources"]:
                            add_related_resources.add(r)

                    if (content != '' and content in cr["Path"][-1]):
                        for r in cr["Resources"]:
                            add_related_resources.add(r)

        print(add_related_resources)
