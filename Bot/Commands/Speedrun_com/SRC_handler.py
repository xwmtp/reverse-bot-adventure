from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Manage_settings.File_manager_factory import get_channel_settings_manager
from Bot.Commands.Speedrun_com.Categories_matcher import Categories_matcher
from Bot.Commands.Speedrun_com.Leaderboard_data import download_leaderboard
from Bot.Utils import make_ordinal, make_request

class SRC_handler(Message_handler):

    def __init__(self):
        super().__init__()
        self.commands = {
            'user_lookup'    : ['!userpb'],
            'pb'             : ['!pb'],
            'wr'             : ['!wr'],
            'leaderboard'    : ['!leaderboard', '!leaderboards', '!src']
        }
        self.categories_matcher = Categories_matcher()
        self.settings_manager = get_channel_settings_manager()

    def handle_message(self, msg, sender, channel):
        split_msg = msg.split(' ')
        command = split_msg[0]
        args_str = ' '.join(split_msg[1:])
        response = None

        matched_category = self.find_category(args_str, channel)

        if command in self.commands['wr']:
            response = self.wr(matched_category)
        if command in self.commands['leaderboard']:
            response = self.src_link(matched_category)
        if command in self.commands['pb']:
            response = self.pb(matched_category, channel)

        if response:
            return response
        elif args_str == "":
            return "Could not find a valid category in the stream title, please provide a category name."
        else:
            return f"Could not find category '{args_str}'"

    def pb(self, matched_category, channel):
        if not matched_category:
            return
        category, values = matched_category
        leaderboard = download_leaderboard(category, values)
        streamer_src = self.lookup_src_name(channel)
        pb_run = leaderboard.get_pb(streamer_src)

        values_str = ', '.join([val.name for val in values])
        category_name = f"{category.name} - {values_str}" if values_str else category.name
        if pb_run:
            return f"{pb_run.player}'s PB for OoT {category_name} is {pb_run.time} ({make_ordinal(pb_run.rank)} place)."
        else:
            return f"No PB found for OoT {category_name} from {streamer_src}."

    def wr(self, matched_category):
        if not matched_category:
            return
        category, values = matched_category
        leaderboard = download_leaderboard(category, values, top=1)
        wr_run = leaderboard.get_run(rank=1)

        values_str = ', '.join([val.name for val in values])
        category_name = f"{category.name} - {values_str}" if values_str else category.name
        if wr_run:
            return f"The current WR for OoT {category_name} is {wr_run.time} by {wr_run.player}."
        else:
            return f"No world record found for OoT {category_name}."

    def src_link(self, matched_category):
        if not matched_category:
            return "https://www.speedrun.com"
        category, _ = matched_category
        return category.weblink

    def find_category(self, args_str, channel):
        if args_str == '':
            stream_title_words = lookup_stream_title(channel[1:]).split()
            for i in range(len(stream_title_words)):
                search_phrase = ' '.join(stream_title_words[i:])
                match = self.categories_matcher.match(search_phrase)
                if match:
                    return match
        else:
            return self.categories_matcher.match(args_str)

    def lookup_src_name(self, channel):
        channel_settings = self.settings_manager.get_setting(channel[1:].lower())
        streamer_src = channel_settings.src_name
        if streamer_src == '':
            return channel[1:]
        else:
            return streamer_src

def lookup_stream_title(channel):
    title = make_request(f"https://decapi.me/twitch/title/{channel}", text_only=True)
    if title:
        return ' '.join(title.split()).lower()

