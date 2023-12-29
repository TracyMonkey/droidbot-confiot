device_serial = "14131FDF600073"
app_path = "/root/documents/droidbot-new/a2dp/a2dp.Vol_169.apk"
droid_output = "/root/documents/droidbot-new/a2dp/"

UI_DIR = "/UI/"
Comparation_DIR = "/Comparation/"
BackButtons_DIR = "/BackButtons/"

Confiot_output = "/root/documents/droidbot-new/a2dp/Confiot"
UI_output = Confiot_output + "/UI"
BackButtons_output = Confiot_output + "/BackButtons/"

##### Influence Type ######
CONFIG_DISABLED = 0
CONFIG_ENABLED = 1
RESOURCE_REMOVED = 2

##### Crawler Limitation ######
# {"activity": {bounds_str : view_id}}
bounds_map = {}
parent_map = {}
# 仅仅只允许同一个center point的view被点击{bounds_limit}次
bounds_limit = 8
parent_limit = 5

##### BackButton ######
# 米家
backs = ([[30, 84], [93, 147]], [[243, 89], [804, 142]], [[813, 111], [837, 125]])
