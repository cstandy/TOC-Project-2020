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
        text = text.lstrip() # Remove leading white space
        prefix = text.split(' ')[0]
        return prefix.rstrip().lower() == "search"

    def is_going_to_add(self, event):
        text = event.message.text
        text = text.lstrip() # Remove leading white space
        prefix = text.split(' ')[0]
        return prefix.rstrip().lower() == "add"

    def is_going_to_list(self, event):
        text = event.message.text
        text = text.lstrip() # Remove leading white space
        return text.rstrip().lower() == "list"

    def is_going_to_help(self, event):
        text = event.message.text
        text = text.lstrip() # Remove leading white space
        prefix = text.split(' ', 1)[0]
        return prefix.lower() == "help"

    def is_going_to_show(self, event):
        text = event.message.text
        text = text.lstrip() # Remove leading white space
        prefix = text.split(' ', 1)[0]
        return prefix.lower() == "show"

    def is_going_to_erase(self, event):
        text = event.message.text
        text = text.lstrip() # Remove leading white space
        prefix = text.split(' ')[0]
        return prefix.lower() == "erase"

    # Auto-binding callback method with 'on_enter_' prefix
    def on_enter_search(self, event):
        print("I'm entering search state")

        # Get time-zone input
        text = event.message.text
        try:
            postfix = text.split(' ')[1].rstrip()
        except:
            info = "Invalid input, usage:\n"
            info = info + "search [option]\n"
            info = info + "- option: all or time-zone\n"
            info = info + "e.g. search all\n"
            info = info + "e.g. search US"
            reply_token = event.reply_token
            send_text_message(reply_token, info)
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
                    # Check if the search input is the prefix of the time zone (large region)
                    if (postfix == tz_all[i].split('/')[0]):
                        try:
                            # Remove the prefix region to save word count
                            prefix = tz_all[i].split('/')[0]
                            prefix_len = len(prefix)
                            tz_str = tz_str + tz_all[i][prefix_len:] + '\n'
                        except:
                            tz_str = tz_str + tz_all[i] + '\n'
                    else:
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
            postfix = text.split(' ')[1].rstrip()
        except:
            info = "Invalid input, usage:\n"
            info = info + "add [time-zone]\n"
            info = info + "e.g. add ROC"
            reply_token = event.reply_token
            send_text_message(reply_token, info)
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
            tz_str =  tz_str + '\n' + self.tz_list[i]

        if (valid_in):
            reply = "Add " + postfix + " success!\n\n" + "Tracked:" + tz_str
        else:
            reply = postfix + " is already in the list or is not valid input\n\n" + "Tracked:" + tz_str

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

        fmt = "%Y-%m-%d %H:%M"

        # Output all current times based on listed time-zones
        for i in range(len(self.tz_list)):
            cur_time = datetime.now(pytz.timezone(self.tz_list[i]))
            reply = reply + self.tz_list[i] + "\n" + cur_time.strftime(fmt) + "\n"
        reply = reply.rstrip() # Remove tailing new line

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
        text = event.message.text

        try:
            # Try to get the cmd from 'help cmd'
            postfix = text.split(' ')[1].rstrip()
            if (postfix == 'list'):
                info = info + "list\n"
                info = info + "e.g. list"
            elif (postfix == 'search'):
                info = info + "search [option]\n"
                info = info + "- option: all or time-zone\n"
                info = info + "e.g. search all\n"
                info = info + "e.g. search US"
            elif (postfix == 'add'):
                info = info + "add [time-zone]\n"
                info = info + "e.g. add ROC"
            elif (postfix == 'show'):
                info = info + "show [time-zone] [time]\n"
                info = info + "e.g. show Tokyo 1600-02-29 13:56"
            elif (postfix == 'erase'):
                info = info + "erase [option]\n"
                info = info + "- option: all or time-zone\n"
                info = info + "e.g. erase all\n"
                info = info + "e.g. erase Tokyo"
        except:
            # If the command is simply 'help'
            info = info + "- list: List tracked time zones with current time.\n"
            info = info + "- search [option]: List all avaliable time-zone.\n"
            info = info + "- add [time-zone]: Add time zone.\n"
            info = info + "- show [time-zone]&[time]: Show specific time.\n"
            info = info + "- erase [option]: Erase some or all tracked time zones.\n"
            info = info + "- help [cmd]: Search for the usage of a command."

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
        try:
            tz_in = text.split(' ', 2)[1]
            time_in = text.split(' ', 2)[2]
        except:
            info = "Invalid input, usage:\n"
            info = info + "show [time-zone] [time]\n"
            info = info + "e.g. show Tokyo 1600-02-29 13:56"
            reply_token = event.reply_token
            send_text_message(reply_token, info)
            self.go_back()

        fmt = "%Y-%m-%d %H:%M"
        
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
            info = "Invalid input, usage:\n"
            info = info + "show [time-zone] [time]\n"
            info = info + "e.g. show Tokyo 1600-02-29 13:56"
            reply = info
        else:
            for i in range(len(self.tz_list)):
                spc_time = dt.astimezone(pytz.timezone(self.tz_list[i]))
                reply = reply + self.tz_list[i] + "\n" + spc_time.strftime(fmt) + '\n'
            reply = reply.rstrip() # Remove tailing new line
        
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
            postfix = text.split(' ')[1].rstrip()
        except:
            info = "Invalid input, usage:\n"
            info = info + "erase [option]\n"
            info = info + "- option: all or time-zone\n"
            info = info + "e.g. erase all\n"
            info = info + "e.g. erase Tokyo"
            reply_token = event.reply_token
            send_text_message(reply_token, info)
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
        reply = 'Erase success!\n\nTracked:'
        for i in range(len(self.tz_list)):
            reply =  reply + '\n' + self.tz_list[i]

        # Sent reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_erase(self):
        print("Leaving erase state")