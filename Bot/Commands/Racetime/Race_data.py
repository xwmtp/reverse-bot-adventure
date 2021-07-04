from dataclasses import dataclass
from typing import List
import datetime as dt
import isodate

def parse_race_data(data):
    entrants = [parse_entrant_data(entrant_data) for entrant_data in data['entrants']]
    return Race(game=data['category']['short_name'],
                category=data['goal']['name'],
                status=data['status']['value'],
                url=data['url'],
                ended_at=data['ended_at'],
                info=data['info'],
                entrants=entrants)

def parse_entrant_data(data):
    if data['status']['value'] == 'done':
        return Entrant(data['user']['name'], data['status']['value'], data['place'], data['finish_time'])
    else:
        return Entrant(data['user']['name'], data['status']['value'])


@dataclass()
class Entrant:
    name: str
    status: str
    rank: int = 99999
    finish_time_iso: str = None

    def get_finish_time(self):
        parsed_time = isodate.parse_duration(self.finish_time_iso)
        return dt.timedelta(seconds = parsed_time.seconds)


    def __str__(self):
        str = self.name
        if self.rank and self.finish_time_iso:
            str = f"{self.rank}. " + str + f" {(self.get_finish_time())}"
        for status in ['dnf', 'dq']:
            if self.status == status:
                str += f" ({status})"
        return str


@dataclass
class Race:
    game: str
    category: str
    info: str
    url: str
    ended_at: str
    status: str
    entrants: List[Entrant]

    def __str__(self):
        return f"{self.game} - {self.category} racetime.gg{self.url} {self.get_string_entrants()}"

    def get_string_entrants(self):
        entrants_strings = [str(e) for e in sorted(self.entrants, key=lambda e: e.rank)]
        return f"{len(self.entrants)} entrants: {' | '.join(entrants_strings)}"

    def active(self):
        return self.status not in ['cancelled', 'finished']

    def ended_at_time(self):
        if not self.ended_at:
            return
        return dt.datetime.strptime(self.ended_at, "%Y-%m-%dT%H:%M:%S.%fZ")

    def ended_recently(self, hour_limit):
        ended_at_time = self.ended_at_time()
        if not ended_at_time:
            return False
        now = dt.datetime.utcnow()
        return now < ended_at_time + dt.timedelta(hours=hour_limit)
