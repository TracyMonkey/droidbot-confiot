import re
import sys, os
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser, Node

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ASTParser:

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
        #             nid: {
        #                 "type": "",
        #                 "text": "",
        #             }
        #         },
        #     }
        # }
        self.resources = {}
        self.plugin_file = plugin_file
        self.raw_code = None

        self.PY_LANGUAGE = Language(tsjavascript.language())
        self.parser = Parser(self.PY_LANGUAGE)

        code = None
        with open(self.plugin_file, "r", encoding="utf-8") as f:
            code = f.read().encode('utf-8')
        if (code):
            self.raw_code = code

    def start_parser(self):
        self.get_resources()
        for id in self.resources:
            self.resources[id]["node"] = self.init_tree_sitter(self.resources[id]["raw"])

    def init_tree_sitter(self, raw) -> Node:
        tree = self.parser.parse(raw.encode('utf-8'))
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
    def get_elements(self, resouce_id):
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
        node = self.resources[resouce_id]["node"]
        elements = {}
        eid = 0

        matches = self.query(query, node)
        print(matches)

    def get_navigations(self, resouce_id):
        raw = self.resources[resouce_id]["raw"]

        pass

    # 获取每个resource内的interactions
    def get_interactions(s):
        pass


if __name__ == '__main__':
    parser = ASTParser(BASE_DIR + "/javascript/main.bundle")
    parser.start_parser()
    parser.get_elements(10001)
