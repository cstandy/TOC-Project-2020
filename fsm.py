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

    def is_going_to_help(self, event):
        text = event.message.text
        return text.lower() == "help"

    def is_going_to_show(self, event):
        text = event.message.text
        prefix = text[:4]
        return prefix.lower() == "show"

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
        valid_in = False

        for i in range(len(pytz.all_timezones)):
            if postfix in tz_all[i]:
                if tz_all[i] not in self.tz_list:
                    valid_in = True
                    self.tz_list.append(tz_all[i])

        tz_str = ''

        for i in range(len(self.tz_list)):
            tz_str = tz_str + self.tz_list[i] + '\n'

        if (valid_in):
            reply = "Add " + postfix + " success!\n" + "Tracking:\n" + tz_str
        else:
            reply = postfix + " is already in the list or is not valid input\n" + "Tracking:\n" + tz_str

        reply_token = event.reply_token
        send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_add(self):
        print("Leaving add state")

    def on_enter_list(self, event):
        tz_str = ''

        fmt = "%Y-%m-%d %H:%M:%S"

        for i in range(len(self.tz_list)):
            cur_time = datetime.now(pytz.timezone(self.tz_list[i]))
            tz_str = tz_str + self.tz_list[i] + "\n" + cur_time.strftime(fmt) + '\n'
        
        reply_token = event.reply_token
        send_text_message(reply_token, "Current time:\n" + tz_str)
        self.go_back()

    def on_exit_list(self):
        print("Leaving list state")

    def on_enter_help(self, event):
        
        info = "Usage:\n"
        info = info + "- search: list all avaliable time-zone (currently Asia)\n"
        info = info + "- add [time-zone]: add time zone\n"
        info = info + "- list: list tracking time zones with current time\n"
        info = info + "- show %Y-%m-%d %H:%M:%S: show specific time"
        info = info + "- help: get this message again\n"

        reply_token = event.reply_token
        send_text_message(reply_token, info)
        self.go_back()

    def on_exit_help(self):
        print("Leaving help state")

    def on_enter_show(self, event):
        text = event.message.text
        postfix = text[5:]
        fmt = "%Y-%m-%d %H:%M:%S"
        dt = datetime.strptime(postfix, fmt)

        tz_str = ''

        for i in range(len(self.tz_list)):
            spc_time = dt.astimezone(pytz.timezone(self.tz_list[i]))
            tz_str = tz_str + self.tz_list[i] + "\n" + spc_time.strftime(fmt) + '\n'
        
        reply_token = event.reply_token
        send_text_message(reply_token, "Specific time:\n" + tz_str)
        self.go_back()

    def on_exit_show(self):
        print("Leaving show state")
