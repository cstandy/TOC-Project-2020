from transitions.extensions import GraphMachine

from utils import send_text_message, send_button_message

import pytz # python time zone package
from datetime import datetime # time processing

# Line API for bottom template
from linebot.models import TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

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
        '''
        Search function: Search in all avaliable time zones in hierarchy.
        For 'search all', only list regions or special areas.
        For 'search region', match all the string with 'region' in avaliable time zones.
        While the output is too large to send, reply to user.
        '''
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
                    # Check also tz_all[i] is in the form 'region/location', e.g. 'US/Pacific'
                    # not just a single location, e.g. 'ROC' since ROC == ROC.split('/')
                    if (postfix == tz_all[i].split('/')[0] and '/' in tz_all[i]):
                        # Remove the prefix region to save word count
                        prefix = tz_all[i].split('/')[0]
                        prefix_len = len(prefix)
                        tz_str = tz_str + tz_all[i][prefix_len:] + '\n'
                        # Notice that if list[i] end with '/', this action might
                        # add an empty string in str. However, here it is not a case.

                    else:
                        tz_str = tz_str + tz_all[i] + '\n'

        # Send reply message
        reply_token = event.reply_token
        if (len(tz_str) <= 0 or len(tz_str) >= 2000):
            send_text_message(reply_token, "Output is out of range (not in 0-2000).")
        else:
            tz_str = tz_str.rstrip()
            send_text_message(reply_token, tz_str)
        self.go_back()

    def on_exit_search(self):
        print("Leaving search state")

    def on_enter_add(self, event):
        '''
        Enable user to add time zone to track (once a time).
        Like 'search' option, match the argument with all avaliable time zones.
        '''
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
            reply = "Add " + postfix + " success!"
            tz_str = "Tracked:" + tz_str
        else:
            reply = postfix + " is already in the list or is not valid input."
            tz_str = "Tracked:" + tz_str

        # Send reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Output is out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply, tz_str)
        self.go_back()

    def on_exit_add(self):
        print("Leaving add state")

    def on_enter_list(self, event):
        '''
        Provide the basic function of time converter: Check current time of
        tracked time zones.
        '''
        print("I'm entering list state")
        reply = ''

        fmt = "%Y-%m-%d %H:%M"

        # Output all current times based on listed time-zones
        for i in range(len(self.tz_list)):
            cur_time = datetime.now(pytz.timezone(self.tz_list[i]))
            reply = reply + self.tz_list[i] + "\n" + cur_time.strftime(fmt) + "\n"
        reply = reply.rstrip() # Remove tailing new line

        # Send reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_list(self):
        print("Leaving list state")

    def on_enter_help(self, event):
        '''
        Use button menu instead of text message to show avaliable options.
        Here is the only part of the code not to use text reply.
        The image is retrived from https://whatsanswer.com/maps/time-zone-map-of-north-america/
        '''
        print("I'm entering help state")
        
        info = ""
        text = event.message.text

        try:
            # Try to get the cmd from 'help cmd'
            postfix = text.split(' ')[1].rstrip()
        except:
            '''
            For supported devices (iOS or Android), show button menu of command info.
            For some unsupported devices (Windows), show following text message.
            For other unsupported devices (Chrome extension), show unsupported message.
            '''
            info = info + "- list: List tracked time zones with current time.\n"
            info = info + "- search [option]: Search in all avaliable time-zone.\n"
            info = info + "- add [time-zone]: Add time zone.\n"
            info = info + "- show [time-zone] [time]: Show specific time.\n"
            info = info + "- erase [option]: Erase some or all tracked time zones.\n"
            info = info + "- help [cmd]: Search for the usage of a command."

            # Create button menu
            buttons = [TemplateSendMessage(
                alt_text=info, # Show if the button function is not avaliable
                template=ButtonsTemplate(
                    thumbnail_image_url='https://upload.cc/i1/2019/12/10/KdvL7Y.jpg',
                    title='Help Menu',
                    text='Tap to see what I can do!',
                    actions=[
                        MessageTemplateAction(
                            label='List',
                            text='help list'
                        ),
                        MessageTemplateAction(
                            label='Search',
                            text='help search'
                        ),
                        MessageTemplateAction(
                            label='Add',
                            text='help add'
                        )
                    ],
                    default_action=MessageTemplateAction(label='help', text='help')
                )
            ),TemplateSendMessage(
                alt_text=info, # Show if the button function is not avaliable
                template=ButtonsTemplate(
                    text='Tap to see what I can do!',
                    actions=[
                        MessageTemplateAction(
                            label='Show',
                            text='help show'
                        ),
                        MessageTemplateAction(
                            label='Erase',
                            text='help erase'
                        ),
                        MessageTemplateAction(
                            label='Help',
                            text='help'
                        )
                    ],
                    default_action=MessageTemplateAction(label='help', text='help')
                )
            )
            ]

            # Send option message (button menu)
            reply_token = event.reply_token
            send_button_message(reply_token, buttons)
        else:
            '''
            For the command 'help cmd', get the postfix and reply the
            description and usage
            '''
            if (postfix == 'list'):
                info = info + "List tracked time zones with current time.\n\n"
                info = info + "Usage: list\n\n"
                info = info + "e.g. list"
            elif (postfix == 'search'):
                info = info + "Search in all avaliable time-zone.\n\n"
                info = info + "Usage: search [option]\n"
                info = info + "- option: all or time-zone\n\n"
                info = info + "e.g. search all\n"
                info = info + "e.g. search US"
            elif (postfix == 'add'):
                info = info + "Add time zone.\n\n"
                info = info + "Usage: add [time-zone]\n\n"
                info = info + "e.g. add ROC"
            elif (postfix == 'show'):
                info = info + "Show specific time.\n\n"
                info = info + "Usage: show [time-zone] [time]\n\n"
                info = info + "e.g. show Tokyo 1600-02-29 13:56"
            elif (postfix == 'erase'):
                info = info + "Erase some or all tracked time zones.\n\n"
                info = info + "Usage: erase [option]\n"
                info = info + "- option: all or time-zone\n\n"
                info = info + "e.g. erase all\n"
                info = info + "e.g. erase Tokyo"
            else:
                info = "Not a valid command, use 'help' to see what I can do!")
            # Send text message
            reply_token = event.reply_token
            send_text_message(reply_token, info)
        
        self.go_back()

    def on_exit_help(self):
        print("Leaving help state")

    def on_enter_show(self, event):
        '''
        Provide extended function of time zone converter:
           Show the time of all tracked time zone based on specific time in
           certain time zone.
        '''
        print("I'm entering show state")

        input_failed = False
        dst_failed = False # Daylight saving time error notifier
        dst_info = ''
        info = ''
        reply = ''

        # Input string pre-processing
        text = event.message.text
        try:
            tz_in = text.split(' ', 2)[1]
            time_in = text.split(' ', 2)[2]
        except:
            input_failed = True
            
            info = info + "Invalid input\n\n"
            info = info + "Usage: show [time-zone] [time]\n\n"
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
                # dt = dt.replace(tzinfo=pytz.timezone(tz_in))
                '''
                Due to the historical reason, tzinfo will have offset 
                Reference: Mar 11th, 1911 Paris Time Change
                    https://www.timeanddate.com/time/change/france/paris?year=1911
                Based on pytz document, localize() must be used to solve this offset
                '''
                dt = pytz.timezone(tz_in).localize(dt, is_dst=None)
            except pytz.InvalidTimeError as e:
                '''
                Due to the argument is_dst=None in localize(), there might be errors in
                daylight saving time boundaries. The first one is ambiguous time, and
                the second one is non-existent time.
                '''
                dst_failed = True
                if (type(e) == pytz.exceptions.AmbiguousTimeError):
                    print('Error: show an ambiguous time due to daylight saving time.')
                    dst_info = "Error: Input an ambiguous time due to daylight saving time.\n"
                if (type(e) == pytz.exceptions.NonExistentTimeError):
                    print('Error: show an non-existent time due to daylight saving time.')
                    dst_info = "Error: Input an non-existent time due to daylight saving time.\n"
            except Exception as e:
                input_failed = True
                info = info + "Invalid input\n\n"
                print(e)

        # Form output string
        if (input_failed or dst_failed):
            info = info + "Usage: show [time-zone] [time]\n\n"
            info = info + "e.g. show Tokyo 1600-02-29 13:56"
            reply = info
        else:
            for i in range(len(self.tz_list)):
                spc_time = dt.astimezone(pytz.timezone(self.tz_list[i]))
                reply = reply + self.tz_list[i] + "\n" + spc_time.strftime(fmt) + '\n'
            reply = reply.rstrip() # Remove tailing new line
        
        # Send reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        elif (dst_failed):
            send_text_message(reply_token, dst_info, reply)
        else:
            send_text_message(reply_token, reply)
        self.go_back()

    def on_exit_show(self):
        print("Leaving show state")

    def on_enter_erase(self, event):
        '''
        Enable the user to remove the time zone which is undesired to track.
        '''
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
        reply = 'Erase success!'
        tz_str = 'Tracked:\n'
        for i in range(len(self.tz_list)):
            tz_str =  tz_str + self.tz_list[i] + '\n'
        tz_str = tz_str.rstrip()

        # Send reply message
        reply_token = event.reply_token
        if (len(reply) <= 0 or len(reply) >= 2000):
            send_text_message(reply_token, "Out of range (not in 0-2000).")
        else:
            send_text_message(reply_token, reply, tz_str)
        self.go_back()

    def on_exit_erase(self):
        print("Leaving erase state")
