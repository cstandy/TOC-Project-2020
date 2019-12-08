from transitions.extensions import GraphMachine

from utils import send_text_message

import pytz # python time zone package

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_search(self, event):
        text = event.message.text
        return text.lower() == "search"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    # Auto-binding callback method with 'on_enter_' prefix
    def on_enter_search(self, event):
        print("I'm entering search state")

        tz_list = pytz.all_timezones
        tz_str = ''

        for i in range(len(pytz.all_timezones)):
            tz_str = tz_str + tz_list[i] + '\n'

        reply_token = event.reply_token
        send_text_message(reply_token, tz_str)
        self.go_back()

    def on_exit_search(self):
        print("Leaving search state")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")
