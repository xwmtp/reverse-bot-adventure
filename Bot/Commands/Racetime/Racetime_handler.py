from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Manage_settings.File_manager_factory import get_channel_settings_manager
from Bot.Commands.Racetime.Race_data import parse_race_data
from Bot.Utils import *
import datetime as dt

GAME_SLUGS = [
    'oot',
    'ootr'
]

class Racetime_handler(Message_handler):
    """Handles messages concerning ongoing Racetime races (live races), with commands like !race, !entrants, etc."""

    def __init__(self):
        super().__init__()
        self.commands = {
            'race': ['!race', '!racetime', '!rtgg'],
            'goal': ['!goal', '!card', '!board', '!chart'],
            'entrants': ['!entrants', '!entrant']
        }
        self.race_urls = {}
        self.settings_manager = get_channel_settings_manager()

    def handle_message(self, msg, sender, channel):
        split_msg = msg.lower().split(' ')
        command = split_msg[0]
        streamer_rtgg = self.lookup_racetime_name(channel)

        if command in self.commands['race']:
            return self.race(streamer_rtgg)
        if command in self.commands['goal']:
            return self.goal(streamer_rtgg)
        if command in self.commands['entrants']:
            return self.entrants(streamer_rtgg)

    def race(self, streamer):
        current_race = self.find_relevant_race(streamer)
        if not current_race:
            return f"No active Racetime race found for {streamer}."
        return str(current_race)

    def goal(self, streamer):
        current_race = self.find_relevant_race(streamer)
        if not current_race:
            return # nothing, in case people want to use their own !goal command outside of racetime races
        if current_race.info:
            return f"{current_race.category} - {current_race.info}"
        else:
            return current_race.category

    def entrants(self, streamer):
        current_race = self.find_relevant_race(streamer)
        if not current_race:
            return # nothing, in case people want to use their own !entrants command outside of racetime races
        return current_race.get_string_entrants()

    def find_relevant_race(self, name):
        race = self.find_live_race(name)
        if race:
            return race
        return self.find_recent_finished_race(name)

    def find_live_race(self, name):
        logging.debug(f"Saved race urls: {self.race_urls}")
        for game in GAME_SLUGS:
            data = make_request(f'https://racetime.gg/{game}/data')
            if not data:
                return
            for race in data['current_races']:
                race_data = make_request(f"https://racetime.gg{race['data_url']}")
                entrant_names = [e['user']['name'].lower() for e in race_data['entrants']]
                if name.lower() in entrant_names:
                    if race_data["status"]["value"] not in ['cancelled', 'finished']:
                        self.race_urls[name.lower()] = race_data['url']
                        return parse_race_data(race_data)

    def find_recent_finished_race(self, name):
        if name.lower() not in self.race_urls:
            return
        logging.debug(f"Looking at finished race for {name}. Current saved races: {self.race_urls}")
        url = self.race_urls[name.lower()]
        data = make_request(f"https://racetime.gg{url}/data")
        if not data or data['status']["value"] not in ['cancelled', 'finished'] or name.lower() not in [e['user']['name'].lower() for e in data['entrants']]:
            del self.race_urls[name.lower()]
            return
        ended_at = dt.datetime.strptime(data['ended_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        now = dt.datetime.utcnow()
        if now < ended_at + dt.timedelta(hours=1):
            return parse_race_data(data)
        else:
            del self.race_urls[name.lower()]


    def lookup_racetime_name(self, channel):
        channel_setting = self.settings_manager.get_setting(channel[1:].lower())
        streamer_rtgg = channel_setting.racetime_name
        if streamer_rtgg == '':
            return channel[1:]
        else:
            return streamer_rtgg
