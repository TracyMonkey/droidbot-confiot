device_serial = "192.168.31.121:5555"

# app_path = "/root/documents/droidbot-new/a2dp/a2dp.Vol_169.apk"
# droid_output = "/root/documents/droidbot-new/a2dp/"
app_path = "/root/documents/Output/mihome/mihome.apk"
droid_output = "/root/documents/Output/mihome/mihome-smartscale-guest/result"

Confiot_output = f"{droid_output}/Confiot"
UI_output = Confiot_output + "/UI/"
Static_comparation_output = Confiot_output + "/Comparation/"

##### Screen Capture resolution for GPT ######
resol_x = 230
resol_y = 512

##### UI Changed Type ######
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
