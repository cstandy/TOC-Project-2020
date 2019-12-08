from transitions.extensions import GraphMachine

from utils import send_text_message

import pytz # python time zone package

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_search(self, event):
        text = event.message.text
        return text.lower() == "search"

    def is_going_to_add(self, event):
        text = event.message.text
        prefix = text[:3]
        return prefix.lower() == "add"

    # Auto-binding callback method with 'on_enter_' prefix
    def on_enter_search(self, event):
        print("I'm entering search state")

        tz_all = pytz.all_timezones
        tz_str = ''

        for i in range(len(pytz.all_timezones)):
            if "Asia" in tz_all[i]:
                tz_str = tz_str + tz_all[i] + '\n'

        reply_token = event.reply_token
        send_text_message(reply_token, tz_str)
        self.go_back()

    def on_exit_search(self):
        print("Leaving search state")

    def on_enter_add(self, event):
        print("I'm entering add state")

        text = event.message.text
        postfix = text[4:]

        tz_all = pytz.all_timezones
        tz_list = []

        for i in range(len(pytz.all_timezones)):
            if postfix in tz_all[i]:
                tz_list.append(tz_all[i])

        tz_str = ''

        for i in range(len(tz_list)):
                tz_str = tz_str + tz_list[i] + '\n'

        reply_token = event.reply_token
        send_text_message(reply_token, "Add " + postfix + " success!")
        send_text_message(reply_token, tz_str)
        self.go_back()

    def on_exit_add(self):
        print("Leaving add state")
