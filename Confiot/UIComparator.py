import difflib
import xml.dom.minidom
import xmldiff.main as xml_diff
import settings
import os

from xmldiff import formatting
from bs4 import BeautifulSoup


class UIComparator:

    def __init__(self, first_option: str, second_option: str):
        self.Confiot_output = settings.Confiot_output
        self.first_option = first_option
        self.second_option = second_option
        self.old_hierarchy_path = self.Confiot_output + settings.UI_DIR + first_option
        self.new_hierarchy_path = self.Confiot_output + settings.UI_DIR + second_option
        self.compare_output_path = self.Confiot_output + settings.Comparation_DIR
        if (not os.path.exists(self.compare_output_path)):
            os.makedirs(self.compare_output_path)

    def format_xml(self, xml_string):
        # 创建DOM解析器
        dom_parser = xml.dom.minidom.parseString(xml_string)
        # 获取格式化后的XML字符串
        formatted_xml = dom_parser.toprettyxml(indent="    ")
        return formatted_xml

    # detect the added nodes
    def UI_config_add(self, differences):

        pass

    def compare_xml_files(self, old_file, new_file):
        self.compare_xml_files2(old_file, new_file,
                                self.compare_output_path + self.first_option + "_to_" + self.second_option + ".html")

    def compare_xml_files_with_xmldiff(self, old_file, new_file):
        old_fp = None
        new_fp = None
        with open(old_file, 'r', encoding='UTF-8') as f:
            old_fp = self.format_xml(f.read())
        with open(new_file, 'r', encoding='UTF-8') as f:
            new_fp = self.format_xml(f.read())
        if old_fp is None or new_fp is None:
            print("[ERR]: cannot open file: " + old_file + " or " + new_file)
            return

        formatter = formatting.DiffFormatter()
        differences = xml_diff.diff_texts(old_fp,
                                          new_fp,
                                          diff_options={
                                              "F": 0.1,
                                              "ratio_mode": "accurate"
                                          },
                                          formatter=formatter)

        print(differences)

        return differences

    def compare_xml_files_with_difflib(self, old_file, new_file, output_file):
        old_fp = None
        new_fp = None
        with open(old_file, 'r', encoding='UTF-8') as f:
            old_fp = self.format_xml(f.read()).split('\n')
        with open(new_file, 'r', encoding='UTF-8') as f:
            new_fp = self.format_xml(f.read()).split('\n')
        if old_fp is None or new_fp is None:
            print("[ERR]: cannot open file: " + old_file + " or " + new_file)
            return

        diff = difflib.HtmlDiff()
        html_diff = diff.make_file(old_fp, new_fp)

        with open(output_file, 'w', encoding='UTF-8') as f:
            f.write(html_diff)


if __name__ == "__main__":
    comparator = UIComparator("A2DP_Start_at_Boot_off", "A2DP_Start_at_Boot_on")

    comparator.compare_xml_files(comparator.old_hierarchy_path + "/819b47c5d517aba591f31b13343d5fde.xml",
                                 comparator.new_hierarchy_path + "/819b47c5d517aba591f31b13343d5fde.xml")
