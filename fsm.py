from transitions.extensions import GraphMachine

from utils import send_text_message

import pytz # python time zone package
from datetime import datetime # time processing

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.tz_list = ['Asia/Taipei']

    def is_going_to_search(self, event):
        text = event.message.text
        return text.lower() == "search"

    def is_going_to_add(self, event):
        text = event.message.text
        prefix = text[:3]
        return prefix.lower() == "add"

    def is_going_to_list(self, event):
        text = event.message.text
        return text.lower() == "list"

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

        for i in range(len(pytz.all_timezones)):
            if postfix in tz_all[i]:
                if tz_all[i] not in self.tz_list:
                    self.tz_list.append(tz_all[i])

        tz_str = ''

        for i in range(len(self.tz_list)):
            tz_str = tz_str + self.tz_list[i] + '\n'

        reply_token = event.reply_token
        send_text_message(reply_token, "Add " + postfix + " success!\n" + "Tracking:\n" + tz_str)
        self.go_back()

    def on_exit_add(self):
        print("Leaving add state")

    def on_enter_list(self, event):
        tz_str = ''

        fmt = "%Y-%m-%d %H:%M:%S %Z%z"

        for i in range(len(self.tz_list)):
            cur_time = datetime.now(pytz.timezone(self.tz_list[i]))
            tz_str = tz_str + self.tz_list[i] + cur_time.strftime(fmt) + '\n'
        
        reply_token = event.reply_token
        send_text_message(reply_token, "Tracking:\n" + tz_str)
        self.go_back()

    def on_exit_list(self):
        print("Leaving list state")
