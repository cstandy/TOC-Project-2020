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

    def is_going_to_erase(self, event):
        text = event.message.text
        prefix = text.split(' ')[0]
        return prefix.lower() == "erase"

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
        print("I'm entering list state")
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
        print("I'm entering help state")
        
        info = ""
        info = info + "Usage:\n"
        info = info + "- list: List tracked time zones with current time.\n"
        info = info + "- search [option]: List all avaliable time-zone.\n"
        info = info + "---- all: List first level.\n"
        info = info + "---- region: Unfold certain region, e.g. US.\n"
        info = info + "- add [time-zone]: Add time zone.\n"
        info = info + "- show [time-zone]&[%Y-%m-%d %H:%M:%S]: Show specific time.\n"
        info = info + "---- %Y-%m-%d %H:%M:%S is the time format.\n"
        info = info + "- erase [option]: Erase some or all tracking time zones.\n"
        info = info + "---- time-zone: Remove certain region or time zone.\n"
        info = info + "---- all: Reset to default.\n"
        info = info + "- help: Get this message again.\n"

        reply_token = event.reply_token
        send_text_message(reply_token, info)
        self.go_back()

    def on_exit_help(self):
        print("Leaving help state")

    def on_enter_show(self, event):
        print("I'm entering show state")

        # Input string pre-processing
        input_failed = False
        text = event.message.text
        postfix = text[5:] # Since format also has a space, the space cannot be used to cut string
        # postfix = text.split(' ')[1] + ' ' + text.split(' ')[2]
        try:
            tz_in = postfix.split('&')[0]
            time_in = postfix.split('&')[1]
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

        # Try to process input string
        if (input_failed == False):
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

    def on_enter_erase(self, event):
        print("I'm entering erase state")
        
        # Get time-zone input
        text = event.message.text
        try:
            postfix = text.split(' ')[1]
        except:
            reply_token = event.reply_token
            send_text_message(reply_token, "Invalid input")
            self.go_back()

        # Erase matched element in tracking list
        tmp_list = []
        if (postfix == 'all'):
            tmp_list = ['Asia/Taipei']
        else:
            for i in range(len(self.tz_list)):
                if postfix not in self.tz_list[i]:
                    tmp_list.append(self.tz_list[i])
        if not tmp_list:
            tmp_list = ['Asia/Taipei']
        self.tz_list = tmp_list

        # Form output string
        reply = 'Erase success!\nTracking:\n'
        for i in range(len(self.tz_list)):
            reply = reply + self.tz_list[i] + '\n'

        # Sent reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_erase(self):
        print("Leaving erase state")