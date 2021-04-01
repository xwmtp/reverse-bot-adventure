from xwillmarktheBot.Commands.Speedrun_stats.Speedrun_com.Category_matcher import Category_matcher
from xwillmarktheBot.Commands.Abstract_Message_Handler import Message_handler
from xwillmarktheBot.Commands.Speedrun_stats import Stream_title
from xwillmarktheBot.Config import Configs
from xwillmarktheBot.Utils import make_ordinal

class SRC_handler(Message_handler):

    def __init__(self):
        super().__init__()
        self.category_matcher = Category_matcher()
        self.commands = {
            'user_lookup'    : ['!userpb'],
            'default_lookup' : ['!pb'],
            'wr'             : ['!wr'],
            'top_times'      : ['!top'],
            'leaderboard'    : ['!leaderboard', '!leaderboards', '!src']
        }

    def handle_message(self, msg, sender):
        split_msg = msg.split(' ')
        command = split_msg[0]
        text = None

        # pb of specific user
        if command in self.commands['wr']:
            text = self.wr(split_msg)
        if command in self.commands['leaderboard']:
            text = self.src_link(split_msg)
        if command in self.commands['user_lookup']:
            text = self.user_pb(split_msg)
        if command in self.commands['default_lookup']:
            text = self.default_pb(split_msg, sender)
        if command in self.commands['top_times']:
            text = self.top_times(split_msg)

        if text:
            return text
        else:
            return 'Category not found.'

    def user_pb(self, split_msg):
        if len(split_msg) < 2:
            return "Please supply a user!"
        user = split_msg[1]
        category = self.get_category(' '.join(split_msg[2:]))
        if category:
            board = category.get_leaderboard(category.selected_subcategory)
            return self.get_pb_text(board, user)

    def default_pb(self, split_msg, sender):
        if Configs.get('respond to user'):
            user = sender
        else:
            user = Configs.get('streamer')
        category = self.get_category(' '.join(split_msg[1:]))
        if category:
            board = category.get_leaderboard(category.selected_subcategory)
            return self.get_pb_text(board, user)

    def wr(self, split_msg):
        category = self.get_category(' '.join(split_msg[1:]))
        if category:
            board = category.get_leaderboard(category.selected_subcategory)
            return self.get_wr_text(board)

    def src_link(self, split_msg):
        category = self.get_category(' '.join(split_msg[1:]))
        if category:
            return category.weblink

    def top_times(self, split_msg):
        if len(split_msg) < 2 or not split_msg[1].isdigit():
            return 'Please supply a number as an argument for !top, i.e. !top 3'
        num = min(int(split_msg[1]),15)
        category = self.get_category(' '.join(split_msg[2:]))
        if category:
            board = category.get_leaderboard(category.selected_subcategory)
            return self.get_top_times_text(board, num)

    def get_top_times_text(self, leaderboard, num):
        texts = []
        for i in range(num):
            run = leaderboard.get_rank_run(i + 1)
            if run:
                texts.append(f"{i+1}. {run.player} - {run.time}")
            else:
                break
        if not texts:
            return f"No runs found for OoT {leaderboard.name}."
        else:
            return f"Top {num} for OoT {leaderboard.name}: {' | '.join(texts)}"

    def get_pb_text(self, leaderboard, user):
        run = leaderboard.get_user_run(user)
        if run is None:
            return f"No PB found for OoT {leaderboard.name} by {user}."
        return f"{run.player}'s PB for OoT {leaderboard.name} is {run.time} ({make_ordinal(run.rank)} place)."

    def get_wr_text(self, leaderboard):
        run = leaderboard.get_rank_run()
        if run is None:
            return f"No world record found for OoT {leaderboard.name}"
        return f"The current WR for OoT {leaderboard.name} is {run.time} by {run.player}."

    def get_category(self, arguments):
        if arguments == '':
            arguments = Stream_title.get_stream_category()
        category = self.category_matcher.match_category(arguments)
        return category
