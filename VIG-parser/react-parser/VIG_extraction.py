import re
import sys, os
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser, Node

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ASTParser:
    # TODO
    # 1. 通过createStackNavigator提取的screens，如何映射到resource_id
    # 2. navigate("page") 函数参数可能是变量
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
                dependencies = list(map(int, [i for i in r[1].split(',') if i.strip() != '']))
                self.resources[id] = {}
                self.resources[id]["raw"] = raw
                self.resources[id]["dependencies"] = dependencies
            return self.resources
        return None

    def query(self, query, node):
        q = self.PY_LANGUAGE.query(query)
        matches = q.matches(node)
        return matches

    # 获取每个resource对应的elements（递归查询），以及相应的type、text
    def get_elements(self, resource_id):
        query = """
        (call_expression
            function: [
                ((identifier) @function (#match? @function ".*createElement"))
                (member_expression property: ((property_identifier) @function (#match? @function ".*createElement")))
                ]
            .
            arguments: (arguments . (_) @element_type . (_) @element_options . (_)*)
        )
            """
        node = self.resources[resource_id]["node"]
        elements = {}
        eid = 0

        matches = self.query(query, node)

        for m in matches:
            if (m[1]):
                function = m[1]["function"]
                element_type = m[1]["element_type"]
                element_options = m[1]["element_options"]
                self.resources[resource_id]["elements"] = {}
                self.resources[resource_id]["elements"][eid] = m[1]
                eid += 1

        # print(matches)

    def get_Navigator(self):
        screens = {}
        initialRouteName = None

        query_createStackNavigator = '''
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
        navigator_stack = self.query(query_createStackNavigator, self.root_node)

        for m in navigator_stack:
            if (m[1]):
                function = m[1]["function"]
                screens_node = m[1]["screens"]
                initialRouteName = m[1]["initialRouteName"].text.replace(b'"', b'').replace(b"'", b'')

                query_pairs = '''
                (object (pair key: (_) @key value: (_) @value))
                '''
                s = self.query(query_pairs, screens_node)
                for i in s:
                    if (i[1]):
                        key = i[1]["key"].text
                        value = i[1]["value"]
                        screens[key] = value
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
    # parser.get_elements(10004)
    parser.get_Navigator()

    if (not parser.screens or not parser.initialRouteName):
        print("[ERR]: Get Navigator failed")
        sys.exit(1)

    for id in parser.resources:
        nav = parser.get_navigations(id)
        if (nav):
            print(nav)
