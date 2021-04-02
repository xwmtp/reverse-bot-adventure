from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Config import Configs
from Bot.Utils import *
import isodate
import datetime
import pytz

class Race_handler(Message_handler):
    """Handles messages concerning ongoing races (live races), with commands like !race, !entrants, etc."""

    def __init__(self):
        super().__init__()
        self.commands = {
            'race' : ['!race'],
            'card' : ['!card', '!board', '!chart'],
            'goal' : ['!goal'],
            'entrants' : ['!entrants']
        }
        self.live_race = None
        self.latest_racetime_url = None

    def handle_message(self, msg, sender):
        split_msg = msg.lower().split(' ')
        command = split_msg[0]
        self.update_live_race(Configs.get('streamer'))
        if self.live_race is None:
            return "No active SRL or Racetime race found."

        def live_race_commands():
            live_race_groups = ['race', 'goal', 'card', 'entrants']
            return flatten([self.commands[group] for group in live_race_groups])

        # current race
        if command in live_race_commands():
            return self.get_live_race_info(command)

    def update_live_race(self, player):
        # search Racetime.gg
        for game in Configs.get('racetime games'):
            json = readjson(f'https://racetime.gg/{game}/data')
            for race in json['current_races']:
                game_json = readjson(f"https://racetime.gg{race['data_url']}")
                entrants = [e['user']['name'].lower() for e in game_json['entrants']]
                if player.lower() in entrants:
                    self.live_race = LiveRacetimeRace(game_json)
                    self.latest_racetime_url = race['data_url']
                    logging.debug(f'Updated {self.live_race.platform} race {self.live_race.id}')
                    # if the race isn't finished, stop looking
                    if self.live_race.state != 'Complete':
                        return

        # keep showing finished racetime races for 1 hour (after completing you can't find them in the game data anymore)
        if self.live_race and self.live_race.platform == 'racetime':
            game_json = readjson(self.live_race.get_race_link() + '/data')
            if game_json['ended_at']:
                finished_time = isodate.parse_datetime(game_json['ended_at'])
                now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                if now < finished_time + datetime.timedelta(hours=1):
                    logging.debug(f'Updated completed {self.live_race.platform} race {self.live_race.id}')
                    self.live_race = LiveRacetimeRace(game_json)
                    return

        self.live_race = None

    def get_live_race_info(self, command):
        if (command in self.commands['card']) & (self.live_race.type != 'bingo'):
            return "Current race is not a bingo. Use !race or !goal."
        response = ''
        if command in self.commands['goal'] + self.commands['card']:
            response = self.live_race.goal.replace('&amp;','&')
        elif command in self.commands['race']:
            response = self.live_race.get_race_link()
        if (command in self.commands['entrants']) | (Configs.get('print all race entrants') & (command in self.commands['race'])):
            response = f"{response} {self.live_race.get_entrants_string()}"
        return response.strip()
