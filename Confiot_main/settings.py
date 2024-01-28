class settings:
    device_serial = "192.168.31.121:5555"

    # app_path = "/root/documents/droidbot-new/a2dp/a2dp.Vol_169.apk"
    # droid_output = "/root/documents/droidbot-new/a2dp/"
    app_path = "/root/documents/Output/mihome/mihome-smartscale/mihome.apk"
    droid_output = "/root/documents/Output/mihome/mihome-smartscale/guest/result"  #"/root/documents/Output/mihome/mihome-smartscale-guest/result"

    Confiot_output = f"{droid_output}/Confiot"
    UI_output = Confiot_output + "/UI/"
    Static_comparation_output = Confiot_output + "/Comparation/"
    UIHierarchy_comparation_output = Static_comparation_output + "/UIHierarchy/"
    Feasibility_comparation_output = Static_comparation_output + "/Feasibility/"

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
    bounds_limit = 30
    parent_limit = 30

    ##### BackButton ######
    # backs: 匹配中心点举例backs坐标50 pixel距离的views
    # precise_backs: 精准匹配某些views

    # Huawei
    backs = ([[27, 63], [135, 171]], [[37, 164], [106, 233]])
    precise_backs = ([[360, 684], [468, 810]],)

    # 米家
    # backs = ([[30, 84], [93, 147]], [[243, 89], [804, 142]], [[813, 111], [837, 125]])
    # precise_backs = ()

    def __init__(self, device, app_path, droid_output) -> None:
        settings.device_serial = device
        settings.app_path = app_path
        settings.droid_output = droid_output

        settings.Confiot_output = settings.droid_output + "/Confiot/"
        settings.UI_output = settings.Confiot_output + "/UI/"
        settings.Static_comparation_output = settings.Confiot_output + "/Comparation/"
