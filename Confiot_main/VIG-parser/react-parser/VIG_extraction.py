import re
import sys, os
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser, Node
from xml.dom import minidom

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR + "/../../")

from util import *


class ASTParser:
    # Challenges:
    # 1. 通过createStackNavigator提取的screens，如何映射到resource_id
    # 2. navigate("page") 函数参数可能是变量, 并且navigate也可能被其他函数调用
    # 3. Elements中的跳转的函数，也是变量，如何链接Elements与相应的跳转逻辑
    # 4. shared用户的UI 不同的问题

    def __init__(self, plugin_file):
        # {
        #     id: {
        #         "node": None,
        #         "raw": "",
        #         "dependencies": [id1, id2, id3, ...],
        #         "elements": {
        #             eid: {
        #                 "type": "",
        #                 "text": "",
        #             }
        #         },
        #         "navigations": {
        #             eid: {
        #                 "type": "",
        #                 "text": "",
        #             }
        #         },
        #     }
        # }
        self.resources = {}
        self.screens = None
        self.initialRouteName = None
        self.screen_in_resources = []

        # Initialize parameters
        self.plugin_file = plugin_file
        self.raw_code = None
        self.root_node = None

        self.PY_LANGUAGE = Language(tsjavascript.language())
        self.parser = Parser(self.PY_LANGUAGE)

        code = None
        with open(self.plugin_file, "r", encoding="utf-8") as f:
            code = f.read().encode('utf-8')
        if (code):
            self.raw_code = code

        self.root_node = self.init_tree_sitter(self.raw_code)

    def start_parser(self):
        self.get_resources()
        for id in self.resources:
            self.resources[id]["node"] = self.init_tree_sitter(self.resources[id]["raw"])

    def init_tree_sitter(self, raw) -> Node:
        tree = self.parser.parse(raw.encode('utf-8') if isinstance(raw, str) else raw)
        return tree.root_node

    # Note: 部分resource_id 不存在，如_reactNative, 可能是import的库
    def get_resources(self):
        match = re.findall(r'__d\((.*?,[ ]?(\d+),[ ]?\[(.*?)\].*?)\);', self.raw_code.decode(), re.DOTALL)
        if match:
            for r in match:
                raw = r[0]
                id = int(r[1])
                dependencies = list(map(int, [i for i in r[2].split(',') if i.strip() != '']))
                self.resources[id] = {}
                self.resources[id]["raw"] = raw
                self.resources[id]["dependencies"] = dependencies

                if ("createStackNavigator" in raw):
                    self.screen_in_resources.append(id)

            return self.resources
        return None

    def query(self, query, node):
        q = self.PY_LANGUAGE.query(query)
        matches = q.matches(node)
        return matches

    def Node_to_XML(self, node):
        dom = minidom.Document()
        root_node = dom.createElement('UIHierarchy')
        dom.appendChild(root_node)

    def get_text_from_element(self, options, Paras):
        results = {}
        # 1. 通过options获取
        match = re.findall(r'(title|text|name|message):\s*([\'"])(.*?)\2', decode_bytes(options), re.DOTALL)
        for m in match:
            if (len(m) == 3):
                results[m[0]] = m[2]

        # 2. 通过Paras获取
        for p in Paras:
            if (p.type == "string"):
                results["textElement"] = decode_bytes(p.text.replace(b'"', b'').replace(b"'", b''))

        return results

    # 获取每个resource对应的elements（递归查询），以及相应的type、text
    def get_elements(self, node):
        query = """
        (call_expression
            function: [
                ((identifier) @function (#match? @function ".*createElement"))
                (member_expression property: ((property_identifier) @function (#match? @function ".*createElement")))
                ]
            .
            arguments: (arguments . (_) @element_type . (_) @element_options . _* @leftParas )@auguments
        )@CALL
            """

        elements = []
        elements_mapper = {}

        matches = self.query(query, node)

        for m in matches:
            if (m[1]):
                function = m[1]["function"]
                CALL = m[1]["CALL"]
                element_type = m[1]["element_type"].text
                element_options = m[1]["element_options"].text
                leftParas = []
                if ("leftParas" in m[1]):
                    leftParas = m[1]["leftParas"]

                related_texts = self.get_text_from_element(element_options, leftParas)

                elements.append({
                    "identifier": CALL.start_point.row,
                    "tag": element_type,
                    "text": related_texts,
                    "childrens": [],
                    "parent": [],
                    "options": element_options,
                    "paras": leftParas
                })
                elements_mapper[CALL.byte_range] = len(elements) - 1

        # 获取elements的关系
        for idx, e in enumerate(elements):
            paras = e["paras"]
            for child in paras:
                # 寻找当前element e的childrens
                child_query = """
                (call_expression
                    function: [
                        ((identifier) @function (#match? @function ".*createElement"))
                        (member_expression property: ((property_identifier) @function (#match? @function ".*createElement")))
                        ]
                )@CALL
                    """
                child_matchs = self.query(child_query, child)

                min_byte_range = None
                for m in child_matchs:
                    if (m[1]):
                        byte_range = m[1]["CALL"].byte_range
                        if (not min_byte_range):
                            min_byte_range = byte_range
                        elif (min_byte_range[0] > byte_range[0]):
                            min_byte_range = byte_range

                if (min_byte_range):
                    target_element = elements_mapper[min_byte_range]
                    elements[idx]["childrens"].append(target_element)
                    elements[target_element]["parent"] = idx

        # print(elements)

    def get_Navigator(self):
        screens = {}
        initialRouteName = None

        query_getScreens = '''
        (call_expression
            function: [
                ((identifier) @function (#match? @function ".*createStackNavigator"))
                (member_expression property: ((property_identifier) @function (#match? @function ".*createStackNavigator")))
                (parenthesized_expression (sequence_expression (member_expression property: ((property_identifier) @function (#match? @function ".*createStackNavigator")))))
                ]
            .
            arguments: (arguments . (_) @screens . (object . (pair key: (_) value: (_) @initialRouteName)) . (_)*)
        )
        '''

        # 获取screen变量的delcaration
        query_screenRelatedResource_screenvar = '''
        (variable_declaration
            (
                    variable_declarator
                    name:
                    (
                        identifier
                    ) @screenvar
                    value:
                    (_) @value
            )
        )
        '''
        # 根据screen delcaration的right value，获取arrayId
        query_screenRelatedResource_arrayId = '''
        (
            subscript_expression
            object:
            (
                identifier
            ) @identifier
            index:
            (
                number
            ) @arrayId
        )
        '''

        if (not self.screen_in_resources):
            return (None, None)

        screenvars = {}

        screenvars_declaration = self.query(query_screenRelatedResource_screenvar,
                                            self.resources[self.screen_in_resources[0]]["node"])
        for m in screenvars_declaration:
            if (m[1]):
                var_name = m[1]["screenvar"].text
                value = m[1]["value"]

                depend_resource_arrayId = self.query(query_screenRelatedResource_arrayId, value)
                arrayId = -1
                for n in depend_resource_arrayId:
                    if (n[1] and n[1]["identifier"].text == b'_dependencyMap'):
                        if (n[1]["arrayId"].type == "number"):
                            arrayId = int(n[1]["arrayId"].text)
                        break
                if (arrayId != -1):
                    screenvars[var_name] = self.resources[self.screen_in_resources[0]]["dependencies"][arrayId]
                else:
                    for v in screenvars:
                        if (v in value.text):
                            screenvars[var_name] = screenvars[v]
                            break

        navigator_stack = self.query(query_getScreens, self.root_node)

        for m in navigator_stack:
            if (m[1]):
                function = m[1]["function"]
                screens_node = m[1]["screens"]
                initialRouteName = m[1]["initialRouteName"].text.replace(b'"', b'').replace(b"'", b'')

                query_pairs = '''
                (object (pair key: (_) @key value: (member_expression object:(identifier)@object property:(property_identifier)@property)))
                '''
                s = self.query(query_pairs, screens_node)
                for i in s:
                    if (i[1]):
                        key = i[1]["key"].text
                        object = i[1]["object"].text
                        property = i[1]["property"].text

                        target_resource_node = None
                        if (screenvars[object] in self.resources):
                            target_resource_node = self.resources[screenvars[object]]["node"]
                        else:
                            print("[ERR]: screen not in resources", screenvars[object])
                            continue
                        if (property == b'default'):
                            # screens[b"Home"] = (resource_id, Node)
                            screens[key] = (screenvars[object], target_resource_node)
                        # screenvar 相关的node为resource中的一个child node
                        else:
                            # 寻找component：名为property
                            query_property_var = f'(variable_declaration (variable_declarator name:(identifier) @var (#eq? @var "{property.decode()}") value:(_) @value))'
                            property_var = self.query(query_property_var, self.root_node)
                            for pv in property_var:
                                if (pv[1]):
                                    screens[key] = (screenvars[object], pv[1]["value"])
                break

        if (initialRouteName not in screens):
            print("[ERR]: initialRouteName not in screens", initialRouteName, screens)

        self.screens = screens
        self.initialRouteName = initialRouteName
        return (screens, initialRouteName)

    def get_navigations(self, resource_id):
        node = self.resources[resource_id]["node"]
        # [byte, Node]
        navigations = []

        query = """
        (call_expression
            function: [
                ((identifier) @function (#match? @function ".*navigate"))
                (member_expression property: ((property_identifier) @function (#match? @function ".*navigate")))
                (parenthesized_expression (sequence_expression (member_expression property: ((property_identifier) @function (#match? @function ".*navigate")))))
                ]
            .
            arguments: (arguments . (_) @destination)
        )
            """

        matches = self.query(query, node)

        for m in matches:
            if (m[1]):
                dest = m[1]["destination"].text
                if (b'"' in dest or b"'" in dest):
                    dest = dest.replace(b'"', b'').replace(b"'", b'')
                    navigations.append(dest)
                else:
                    navigations.append(m[1]["destination"])

        self.resources[resource_id]["navigations"] = navigations
        return navigations

    # 获取每个resource内的interactions
    def get_interactions(s):
        pass


if __name__ == '__main__':
    parser = ASTParser(BASE_DIR + "/javascript/main.bundle")
    parser.start_parser()
    parser.get_elements(parser.resources[10007]["node"])
    parser.get_Navigator()

    if (not parser.screens or not parser.initialRouteName):
        print("[ERR]: Get Navigator failed")
        sys.exit(1)

    for id in parser.resources:
        nav = parser.get_navigations(id)
        if (nav):
            print(nav)
