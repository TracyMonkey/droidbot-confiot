from collections import deque
import warnings
from PIL import Image, ImageDraw
from openai import OpenAI
from base64 import b64encode
import os
import re


def deprecated(func):

    def wrapper(*args, **kwargs):
        warnings.warn(f"Function {func.__name__} is deprecated.", category=DeprecationWarning)
        return func(*args, **kwargs)

    return wrapper


def draw_rect_with_bounds(file, bounds):
    # 打开图像文件
    image = Image.open(file)

    # 创建一个可绘制对象
    draw = ImageDraw.Draw(image)

    # 定义框的坐标
    x1, y1 = bounds[0]
    x2, y2 = bounds[1]

    # 绘制红色框
    draw.line([(x1, y1), (x2, y1)], fill="red", width=2)  # 上边
    draw.line([(x2, y1), (x2, y2)], fill="red", width=2)  # 右边
    draw.line([(x2, y2), (x1, y2)], fill="red", width=2)  # 下边
    draw.line([(x1, y2), (x1, y1)], fill="red", width=2)  # 左边

    # 保存修改后的图像
    image.save(file)


def png_resize(file, resol_x, resol_y):
    from PIL import Image

    try:
        # 打开图片
        image = Image.open(file)

        # 设置新的分辨率
        new_resolution = (resol_x, resol_y)

        # 改变分辨率
        resized_image = image.resize(new_resolution)

        # 保存图片
        resized_image.save(f"{file}.resize.png")

        return f"{file}.resize"
    except Exception as e:
        print("[ERR]: Failed to resize the image " + file, e)
        return -1


class Node:

    def __init__(self, name, description='', state=''):
        self.name = name
        self.description = description
        self.state = state

    def __str__(self):
        return self.name


class Edge:

    def __init__(self, start_node, end_node, event_strs: list):
        self.start_node = start_node
        self.end_node = end_node
        self.event_strs = event_strs


class DirectedGraph:

    def __init__(self):
        # utg.js中原始的nodes以及edges
        self.utg_nodes = []
        self.utg_edges = []

        # DirectedGraph中的nodes以及edges
        self.nodes = []
        # {"state_str": Node}
        self.nodes_dict = {}

        self.edges = []
        # {"src_node": {"dst_node": ["e1", "e2"]}}
        self.edges_dict = {}
        self.start_node = None

    def add_node(self, node: Node):
        self.nodes.append(node)
        self.nodes_dict[node.name] = node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        if (edge.start_node.name not in self.edges_dict):
            self.edges_dict[edge.start_node.name] = {}

        if (edge.end_node.name not in self.edges_dict[edge.start_node.name]):
            self.edges_dict[edge.start_node.name][edge.end_node.name] = []

        for event in edge.event_strs:
            self.edges_dict[edge.start_node.name][edge.end_node.name].append(event)

    def find_shortest_path(self, node_1: str, node_2: str):

        if node_1 not in self.nodes_dict or node_2 not in self.nodes_dict:
            print("[ERR]: Cannot find node")
            return None

        node_1 = self.nodes_dict[node_1]
        node_2 = self.nodes_dict[node_2]
        # 使用广度优先搜索算法寻找最短路径
        visited = set()
        queue = deque([(node_1, [])])

        while queue:
            current_node, path = queue.popleft()
            if current_node == node_2:
                return path + [current_node]

            if current_node not in visited:
                visited.add(current_node)
                neighbors = self.get_neighbors(current_node)
                for neighbor in neighbors:
                    queue.append((neighbor, path + [current_node]))

        return None

    def get_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge.start_node == node:
                neighbors.append(edge.end_node)
        return neighbors

    @staticmethod
    def draw(graph, output_dir):
        dot_content = "digraph G {\n"

        added_edges = set()

        for edge in graph.edges:
            edge_str = f'  "{edge.start_node.name}" -> "{edge.end_node.name}"'
            if edge_str not in added_edges:
                dot_content += edge_str + "\n"
                added_edges.add(edge_str)
        for node in graph.nodes:
            dot_content += f'  "{node.name}" [label="{node.name}\\n{node.description}"]\n'

        dot_content += "}"

        with open(f"{output_dir}/UITree.dot", "w") as dot_file:
            dot_file.write(dot_content)


class UITree(DirectedGraph):

    def __init__(self):
        # config-tempid
        self.nodes = []

        self.nodes_dict = {}

        # event (config set to a specific value)
        self.edges = []
        # {"src_node": {"dst_node": ["e1"]}}
        self.edges_dict = {}
        self.start_node = None


# 解析GPT返回的mapping
def parse_config_resource_mapping(text):
    ConfigResourceMapper = []

    pattern = re.compile(r'Configuration path: (\[.*?\])\s+Task: (.*?)\s+Related resources: (.*?)', re.DOTALL)
    matches = pattern.findall(text)

    for match in matches:
        try:
            config_path = eval(match[0])  # 使用 eval 将字符串转为列表
            task = match[1]
            related_resources = match[2]

            ConfigResourceMapper.append({"Path": config_path, "Task": task, "Resources": related_resources})
            print("Configuration Path:", config_path)
            print("Task:", task)
            print("Related Resources:", related_resources)
        except Exception as e:
            print(e)

    print(
        "----------------------------------------------------------------------------------------------------------------------------------------------"
    )
    return ConfigResourceMapper


def query_config_resource_mapping(prompt):
    import requests
    api_key = os.environ.get("OPENAI_API_KEY")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # syncxxx: use gpt-4 new model
    payload = {"model": "gpt-4-1106-preview", "messages": [{"role": "user", "content": prompt}]}
    # payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # URL = os.environ['OPENAI_API_KEY']  # NOTE: replace with your own GPT API
    # body = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "stream": True}
    # headers = {'Content-Type': 'application/json', 'path': 'v1/chat/completions'}
    # r = requests.post(url=URL, json=body, headers=headers)
    #return response.content.decode()

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    # 创建有向图
    graph = DirectedGraph()

    # 创建节点
    node_1 = Node("Node 1")
    node_2 = Node("Node 2")
    node_3 = Node("Node 3")
    node_4 = Node("Node 4")
    node_5 = Node("Node 5")

    # 添加节点到图中
    graph.add_node(node_1)
    graph.add_node(node_2)
    graph.add_node(node_3)
    graph.add_node(node_4)
    graph.add_node(node_5)

    # 创建边
    edge_1 = Edge(node_1, node_2)
    edge_2 = Edge(node_1, node_3)
    edge_3 = Edge(node_2, node_3)
    edge_4 = Edge(node_3, node_4)
    edge_5 = Edge(node_4, node_5)
    edge_6 = Edge(node_1, node_5)

    # 添加边到图中
    graph.add_edge(edge_1)
    graph.add_edge(edge_2)
    graph.add_edge(edge_3)
    graph.add_edge(edge_4)
    graph.add_edge(edge_5)
    graph.add_edge(edge_6)

    # 寻找从node_1到node_5的最短路径
    shortest_path = graph.find_shortest_path("Node 1", "Node 5")
    for node in shortest_path:
        print(node)
