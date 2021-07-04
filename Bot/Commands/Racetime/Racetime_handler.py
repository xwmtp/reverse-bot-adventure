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
            'setrace': ['!setrace'],
            'goal': ['!goal', '!card', '!board', '!chart'],
            'entrants': ['!entrants', '!entrant']
        }
        self.race_urls = {}
        self.saved_race = {}
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
        if command in self.commands['setrace']:
            return self.set_race(sender, channel, streamer_rtgg, split_msg)

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

    def set_race(self, sender, channel, streamer, args):
        if channel[1:].lower() != sender.lower():
            return "Only the channel owner can use this command!"
        if len(args) <= 1:
            return "Add an argument with the url of the race to set."
        url = args[1]
        if not url.startswith("https://racetime.gg/"):
            return "Invalid racetime url, example: https://racetime.gg/oot/example-race-1234"
        data = make_request(url + "/data")
        if not data:
            return f"Cannot find race at {url}"
        self.saved_race[streamer.lower()] = url.replace("https://racetime.gg","")
        return f"Saved race {url}, use !race to see information"

    def find_relevant_race(self, name):
        race = self.find_saved_live_race(name)
        if race:
            return race
        race = self.find_live_race(name)
        if race:
            return race
        race = self.find_saved_recent_finished_race(name)
        if race:
            return race
        race = self.find_recent_finished_race(name)
        if race:
            return race

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
                    race = parse_race_data(race_data)
                    if race.active():
                        self.race_urls[name.lower()] = race_data['url']
                        return race

    def find_recent_finished_race(self, name):
        logging.debug(f"Looking at finished race for {name}. Current saved races: {self.race_urls}")
        race = self.retrieve_race_from_dict_url(self.race_urls, name)
        if race and race.ended_recently(hour_limit=1):
            return race

    def find_saved_live_race(self, name):
        race = self.retrieve_race_from_dict_url(self.saved_race, name)
        if race and race.active():
            return race

    def find_saved_recent_finished_race(self, name):
        race = self.retrieve_race_from_dict_url(self.saved_race, name)
        if race and race.ended_recently(hour_limit=1):
            return race

    def retrieve_race_from_dict_url(self, url_dict, name):
        if name.lower() not in url_dict:
            return
        url = url_dict[name.lower()]
        data = make_request(f"https://racetime.gg{url}/data")
        if not data:
            del self.saved_race[name.lower()]
            return
        return parse_race_data(data)


    def lookup_racetime_name(self, channel):
        channel_setting = self.settings_manager.get_setting(channel[1:].lower())
        streamer_rtgg = channel_setting.racetime_name
        if streamer_rtgg == '':
            return channel[1:]
        else:
            return streamer_rtgg
