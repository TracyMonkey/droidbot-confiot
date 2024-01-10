from optparse import OptionParser
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.append(BASE_DIR + "/../")

from Confiot_main.Confiot import ConfiotGuest, ConfiotHost, Confiot
from Confiot_main.settings import settings
from Confiot_main.util import get_ConfigResourceMapper_from_file


def HostInitialization():
    confiot = ConfiotHost()

    # 请求GPT
    ConfigResourceMapper = None
    if (not os.path.exists(settings.Confiot_output + "/ConfigResourceMapping.txt")):
        ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    else:
        ConfigResourceMapper = get_ConfigResourceMapper_from_file(settings.Confiot_output + "/ConfigResourceMapping.txt")
    return confiot


def GuestInitialization():
    confiot = ConfiotGuest()
    confiot.device_connect()

    # 请求GPT
    ConfigResourceMapper = None
    if (not os.path.exists(settings.Confiot_output + "/ConfigResourceMapping.txt")):
        ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    else:
        ConfigResourceMapper = get_ConfigResourceMapper_from_file(settings.Confiot_output + "/ConfigResourceMapping.txt")
    return confiot


def HostRunTask(task, task_state):
    from AutoDroid.droidbot import input_manager
    from AutoDroid.droidbot import input_policy
    from AutoDroid.droidbot import env_manager
    from AutoDroid.droidbot.droidbot import DroidBot
    from AutoDroid.droidbot.droidmaster import DroidMaster

    droidbot = DroidBot(app_path=settings.app_path,
                        device_serial=settings.device_serial,
                        task=task,
                        is_emulator=True,
                        output_dir=settings.droid_output + "/Autodroid/",
                        env_policy=env_manager.POLICY_NONE,
                        policy_name=input_manager.POLICY_TASK,
                        script_path=None,
                        event_interval=2,
                        timeout=input_manager.DEFAULT_TIMEOUT,
                        event_count=input_manager.DEFAULT_EVENT_COUNT,
                        debug_mode=False,
                        keep_app=True,
                        keep_env=True,
                        grant_perm=True,
                        enable_accessibility_hard=True,
                        ignore_ad=True,
                        state=task_state)
    droidbot.start()


def GuestRunAnalysis(host_analyzing_config=""):
    actor = GuestInitialization()
    actor.device_state_replay(host_analyzing_config)
    actor.device_guest_config_walker(host_analyzing_config)
    actor.device.disconnect()


def HostAction():
    # 主人开始task list中的任务
    tasks = {0: [("2. Remove an alarm", "015ba3ec79e0b0f55a19ce31bbc72b503e56184e14e0cef46ad942d8d357f489"),]}

    for pid in tasks:
        for t in tasks[pid]:
            # 主人进行task t
            HostRunTask(t[0], t[1])
            input()


def GuestAction():
    # 主人开始task list中的任务
    tasks = {0: [("2. Remove an alarm", "015ba3ec79e0b0f55a19ce31bbc72b503e56184e14e0cef46ad942d8d357f489"),]}

    for pid in tasks:
        # 对于每条path代表的所有task进行前，完成一遍GuestRunAnalysis
        host_analyzing_config = str(pid)
        GuestRunAnalysis(host_analyzing_config)
        for t in tasks[pid]:
            cleaned_sentence = re.sub(r'[^a-zA-Z0-9 ]', '', t[0])
            task_name = '_'.join(cleaned_sentence.split())
            host_analyzing_config = str(pid) + "_" + task_name

            # 主人进行task t
            # HostRunTask(host, t)
            input()
            # 客人进行app分析
            GuestRunAnalysis(host_analyzing_config)


if __name__ == "__main__":
    # os.environ["https_proxy"] = "http://192.168.72.1:1083"

    # s = settings("14131FDF600073", "/root/documents/Output/Huawei_AI_Life/Huawei.apk",
    #              "/root/documents/Output/Huawei_AI_Life/host/result")
    # # HostActor = HostInitialization()
    # HostAction(None, "2. Remove an alarm", "015ba3ec79e0b0f55a19ce31bbc72b503e56184e14e0cef46ad942d8d357f489")

    parser = OptionParser()
    parser.add_option("-a", "--app-path", dest="app_path", help="The apk path of the target application")
    parser.add_option("-d", "--device", dest="device", help="The device serial")
    parser.add_option("-D", "--droidbot-output", dest="droid_output", help="The output path of droidbot")
    parser.add_option("-H", "--host", dest="host", action="store_true", default=False, help="Host")
    parser.add_option("-G", "--guest", dest="guest", action="store_true", default=False, help="Guest")
    parser.add_option("-b", "--director", dest="director", action="store_true", default=False, help="Director Mode")
    parser.add_option("-c", "--configuration", dest="config", help="Configuration File")

    (options, args) = parser.parse_args()

    s = settings(options.device, options.app_path, options.droid_output)

    HostActor = None
    GuestActor = None

    if (options.host):
        HostActor = HostInitialization()
        HostRunTask(None, "2. Remove an alarm", "015ba3ec79e0b0f55a19ce31bbc72b503e56184e14e0cef46ad942d8d357f489")
    elif (options.guest):
        GuestAction()
