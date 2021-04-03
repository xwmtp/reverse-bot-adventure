from dataclasses import dataclass
from typing import List

def parse_race_data(data):
    entrants = [parse_entrant_data(entrant_data) for entrant_data in data['entrants']]
    return Race(game=data['category']['short_name'],
                category=data['goal']['name'],
                url=data['url'],
                info=data['info'],
                entrants=entrants)

def parse_entrant_data(data):
    if data['status'] == 'done':
        return Entrant(data['name'], data['status']['value'], data['place'], data['finish_time'])
    else:
        return Entrant(data['name'], data['status']['value'])


@dataclass()
class Entrant:
    name: str
    status: str
    rank: int = None
    finish_time: str = None

    def __str__(self):
        str = self.name
        if self.rank and self.finish_time:
            str = f"{self.rank}. " + str + f" {(self.finish_time)}"
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
    entrants: List[Entrant]

    def __str__(self):
        return f"{self.game} - {self.category} ({self.url}): {self.get_string_entrants()}"

    def get_string_entrants(self):
        entrants_strings = [str(e) for e in sorted(self.entrants, key=lambda e: e.rank)]
        return ' | '.join(entrants_strings)
