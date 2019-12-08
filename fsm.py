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
        prefix = text.split(' ')[0]
        return prefix.lower() == "search"

    def is_going_to_add(self, event):
        text = event.message.text
        prefix = text.split(' ')[0]
        return prefix.lower() == "add"

    def is_going_to_list(self, event):
        text = event.message.text
        return text.lower() == "list"

    def is_going_to_help(self, event):
        text = event.message.text
        return text.lower() == "help"

    def is_going_to_show(self, event):
        text = event.message.text
        prefix = text.split(' ')[0]
        return prefix.lower() == "show"

    # Auto-binding callback method with 'on_enter_' prefix
    def on_enter_search(self, event):
        print("I'm entering search state")

        # Get time-zone input
        text = event.message.text
        try:
            postfix = text.split(' ')[1]
        except:
            reply_token = event.reply_token
            send_text_message(reply_token, "Invalid input")
            self.go_back()

        tz_all = pytz.all_timezones
        tz_str = ''

        # List all avaliable time-zones
        if (postfix == 'all'):
            for i in range(len(tz_all)):
                if '/' in tz_all[i]:
                    if tz_all[i].split('/')[0] not in tz_str:
                        tz_str = tz_str + tz_all[i].split('/')[0] + '/\n'
                else:
                    tz_str = tz_str + tz_all[i] + '\n'
        else:
            for i in range(len(tz_all)):
                if postfix in tz_all[i]:
                    tz_str = tz_str + tz_all[i] + '\n'

        # Sent reply message
        reply_token = event.reply_token
        send_text_message(reply_token, tz_str)
        self.go_back()

    def on_exit_search(self):
        print("Leaving search state")

    def on_enter_add(self, event):
        print("I'm entering add state")

        # Get time-zone input
        text = event.message.text
        try:
            postfix = text.split(' ')[1]
        except:
            reply_token = event.reply_token
            send_text_message(reply_token, "Invalid input")
            self.go_back()

        tz_all = pytz.all_timezones
        valid_in = False

        # Check input time-zone is avaliable and not already in list
        for i in range(len(pytz.all_timezones)):
            if postfix in tz_all[i]:
                if tz_all[i] not in self.tz_list:
                    valid_in = True
                    self.tz_list.append(tz_all[i])

        # Form output string
        tz_str = ''
        for i in range(len(self.tz_list)):
            tz_str = tz_str + self.tz_list[i] + '\n'

        if (valid_in):
            reply = "Add " + postfix + " success!\n" + "Tracking:\n" + tz_str
        else:
            reply = postfix + " is already in the list or is not valid input\n" + "Tracking:\n" + tz_str

        # Sent reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_add(self):
        print("Leaving add state")

    def on_enter_list(self, event):
        reply = ''

        fmt = "%Y-%m-%d %H:%M:%S"

        # Output all current times based on listed time-zones
        for i in range(len(self.tz_list)):
            cur_time = datetime.now(pytz.timezone(self.tz_list[i]))
            reply = reply + self.tz_list[i] + "\n" + cur_time.strftime(fmt) + '\n'
        
        # Sent reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_list(self):
        print("Leaving list state")

    def on_enter_help(self, event):
        
        info = "Usage:\n"
        info = info + "- search [region]: list all avaliable time-zone\n"
        info = info + "---- region: all: list first level\n"
        info = info + "---- region: eg. US"
        info = info + "- add [time-zone]: add time zone\n"
        info = info + "- list: list tracking time zones with current time\n"
        info = info + "- show [time-zone]&[%Y-%m-%d %H:%M:%S]: show specific time"
        info = info + "- help: get this message again\n"

        reply_token = event.reply_token
        send_text_message(reply_token, info)
        self.go_back()

    def on_exit_help(self):
        print("Leaving help state")

    def on_enter_show(self, event):
        # Input string pre-processing
        text = event.message.text
        postfix = text.split(' ')[0]
        try:
            tz_in = postfix.split('&')[0]
            time_in = postfix.split(' ')[1]
        except:
            reply_token = event.reply_token
            send_text_message(reply_token, "Invalid input")
            self.go_back()

        fmt = "%Y-%m-%d %H:%M:%S"
        
        # Search input timezone
        tz_all = pytz.all_timezones
        for i in range(len(pytz.all_timezones)):
            if tz_in in tz_all[i]:
                tz_in = tz_all[i]
                break

        input_failed = False
        # Try to process input string
        try:
            dt = datetime.strptime(time_in, fmt)
            dt = dt.replace(tzinfo=pytz.timezone(tz_in))
        except Exception as e:
            print(e)
            input_failed = True

        reply = ''

        # Form output string
        if (input_failed):
            reply = 'input failed'
        else:
            for i in range(len(self.tz_list)):
                spc_time = dt.astimezone(pytz.timezone(self.tz_list[i]))
                reply = reply + self.tz_list[i] + "\n" + spc_time.strftime(fmt) + '\n'
        
        # Sent reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_show(self):
        print("Leaving show state")
