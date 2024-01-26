from optparse import OptionParser
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.append(BASE_DIR + "/../")

from Confiot_main.Confiot import ConfiotGuest, ConfiotHost, Confiot
from Confiot_main.settings import settings
from Confiot_main.util import get_ConfigResourceMapper_from_file


def HostInitialization(path=''):
    confiot = ConfiotHost()
    full_mapping_path = ''
    filtered_mapping_path = ''

    if (path != ''):
        full_mapping_path = path + "/ConfigResourceMapping.txt"
        filtered_mapping_path = path + "/FilteredConfigResourceMapping.txt"
    else:
        full_mapping_path = settings.Confiot_output + "/ConfigResourceMapping.txt"
        filtered_mapping_path = settings.Confiot_output + "/FilteredConfigResourceMapping.txt"

    # 请求GPT
    if (not os.path.exists(full_mapping_path)):
        confiot.ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    else:
        confiot.ConfigResourceMapper = get_ConfigResourceMapper_from_file(full_mapping_path)

    if (os.path.exists(filtered_mapping_path)):
        confiot.FilteredConfigResourceMapper = get_ConfigResourceMapper_from_file(filtered_mapping_path)
    else:
        print("[ERR]: can not find file:", filtered_mapping_path)

    # print(confiot.FilteredConfigResourceMapper)
    return confiot


def GuestInitialization():
    confiot = ConfiotGuest()
    confiot.device_connect()

    if (not os.path.exists(settings.Confiot_output + "/ConfigResourceMapping.txt")):
        confiot.ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    else:
        confiot.ConfigResourceMapper = get_ConfigResourceMapper_from_file(settings.Confiot_output +
                                                                          "/ConfigResourceMapping.txt")

    if (os.path.exists(settings.Confiot_output + "/FilteredConfigResourceMapping.txt")):
        confiot.FilteredConfigResourceMapper = get_ConfigResourceMapper_from_file(settings.Confiot_output +
                                                                                  "/FilteredConfigResourceMapping.txt")
    else:
        print("[ERR]: can not find file:", settings.Confiot_output + "/FilteredConfigResourceMapping.txt")
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


# point用于断点继续开始, replay_point:state_str, walker_point:view_2fb7d047fc22be5efccfd0fa9c96be7b.jpg121
def GuestRunAnalysis(host_analyzing_config="", replay_point='', walker_point=''):
    actor = GuestInitialization()
    if (walker_point != ''):
        actor.device_guest_config_walker(host_analyzing_config, walker_point)
    else:
        actor.device_state_replay(host_analyzing_config, replay_point)
        actor.device_guest_config_walker(host_analyzing_config, walker_point)
    actor.device.disconnect()


def HostAction(hosttasks, task_point=''):
    # 主人开始task list中的任务
    tasks = hosttasks

    for task in tasks:
        for t in task["Tasks"]:
            if (str(task["Id"]) == task_point):
                # 主人进行task t
                HostRunTask(t, task["state"])
                break
            else:
                continue


def GuestAction(hosttasks, task_point='', replay_point='', walker_point=''):
    # 主人开始task list中的任务
    tasks = hosttasks

    if (task_point == ''):
        # 对于每条path代表的所有task进行前，完成一遍GuestRunAnalysis
        host_analyzing_config = "000"
        GuestRunAnalysis(host_analyzing_config, replay_point, walker_point)

    begin_flag = False

    if (task_point == ''):
        begin_flag = True

    for task in tasks:
        if (task_point != '' and not begin_flag):
            if (str(task["Id"]) == task_point):
                begin_flag = True
            else:
                continue
        if (begin_flag):
            for t in task["Tasks"]:
                cleaned_sentence = re.sub(r'[^a-zA-Z0-9 ]', '', t)
                task_name = '_'.join(cleaned_sentence.split())
                host_analyzing_config = str(task["Id"]) + "_" + task_name

                # 主人进行task t
                # HostRunTask(host, t)
                input()
                # 客人进行app分析
                GuestRunAnalysis(host_analyzing_config, replay_point, walker_point)


if __name__ == "__main__":
    os.environ["https_proxy"] = "http://192.168.72.1:1083"

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
    parser.add_option("--task-point", dest="task_point", help="Configuration File")
    parser.add_option("--replay-point", dest="replay_point", help="Configuration File")
    parser.add_option("--walker-point", dest="walker_point", help="Configuration File")

    (options, args) = parser.parse_args()

    s = settings(options.device, options.app_path, options.droid_output)

    HostActor = None
    GuestActor = None

    task_point = ''
    replay_point = ''
    walker_point = ''
    if (options.task_point):
        task_point = str(options.task_point)
    if (options.replay_point):
        replay_point = str(options.replay_point)
    if (options.walker_point):
        walker_point = str(options.walker_point)

    if (options.host):
        HostActor = HostInitialization()
        HostAction(HostActor.FilteredConfigResourceMapper, task_point)
    elif (options.guest):
        GuestInitialization()
        # HostActor = HostInitialization(path=options.droid_output + "/../../host/result/Confiot")
        # GuestAction(HostActor.FilteredConfigResourceMapper,
        #             task_point=task_point,
        #             replay_point=replay_point,
        #             walker_point=walker_point)
