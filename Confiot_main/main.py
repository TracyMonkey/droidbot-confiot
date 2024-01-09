from optparse import OptionParser
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.append(BASE_DIR + "/../")

from Confiot_main.Confiot import ConfiotGuest, ConfiotHost, Confiot
from Confiot_main.settings import settings


def HostInitialization():
    confiot = ConfiotHost()

    # 请求GPT
    ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    return confiot


def GuestInitialization():
    confiot = ConfiotGuest()
    confiot.device_connect()

    # 请求GPT
    ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    return confiot


def HostAction(actor: ConfiotHost, task, state):
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
                        state=state)
    droidbot.start()


def GuestAction(actor: ConfiotGuest, host_analyzing_config=""):
    actor.device_state_replay("naozhong")


def Action(host, guest):
    # 主人开始task list中的任务
    tasks = {"path_1": ["1. Set up an alarm on Huawei AI Speaker", "2. Remove an alarm"]}
    for p in tasks:
        GuestAction(guest)
        for t in tasks[p]:
            HostAction(host, t)
            GuestAction(guest)


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
        # HostActor = HostInitialization()
        HostAction(None, "1. Set up an alarm on Huawei AI Speaker",
                   "015ba3ec79e0b0f55a19ce31bbc72b503e56184e14e0cef46ad942d8d357f489")
    elif (options.guest):
        GuestActor = GuestInitialization()
