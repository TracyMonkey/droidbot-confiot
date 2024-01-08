from optparse import OptionParser
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.append(BASE_DIR + "/../")

from Confiot_main.Confiot import ConfiotGuest, ConfiotHost, Confiot
from Confiot_main.settings import settings


def HostInitialization():
    confiot = ConfiotHost()

    os.environ["https_proxy"] = "http://192.168.72.1:1083"
    # 请求GPT
    ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    return confiot


def GuestInitialization():
    confiot = ConfiotGuest()
    confiot.device_connect()

    os.environ["https_proxy"] = "http://192.168.72.1:1083"
    # 请求GPT
    ConfigResourceMapper = confiot.device_map_config_resource(settings.Confiot_output)
    return confiot


def GuestSingleRun(actor: ConfiotGuest):
    actor.device_state_replay("naozhong")


def Action():
    # 主人开始task list中的任务
    pass


if __name__ == "__main__":

    # s = settings("192.168.31.121:5555", "/root/documents/Output/Huawei_AI_Life/Huawei.apk",
    #              "/root/documents/Output/Huawei_AI_Life/host/result")
    # HostStart()

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

    # guest = GuestInitialization()
    # GuestSingleRun(guest)

    if (options.host):
        HostInitialization()
    elif (options.guest):
        GuestInitialization()
