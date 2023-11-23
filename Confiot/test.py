from Confiot import Confiot

# For test
CONFIG_ANALYZED = "A2DP_Start_at_Boot_off"


def test_goto_state():
    confiot = Confiot()
    confiot.device_connect()

    confiot.parse_event()
    # print(confiot.events)
    confiot.parse_utg()

    while (1):
        target_str = input("state: ")
        if (target_str == '\n' or target_str == ''):
            confiot.device_stop_app()
            break
        confiot.device_to_state(CONFIG_ANALYZED, target_str)


def test_stop_app():
    confiot = Confiot()
    confiot.device_connect()

    confiot.device_stop_app()


def test_state_walker():
    confiot = Confiot()
    confiot.device_connect()

    confiot.parse_event()
    # print(confiot.events)
    confiot.parse_utg()

    confiot.device_state_walker(CONFIG_ANALYZED)


if __name__ == "__main__":
    test_state_walker()
