from dataclasses import dataclass

from Bot.Utils import make_request, seconds_to_hhmmss


def download_leaderboard(category, var, top=None):
    parameters = []
    if var:
        parameters.append(f"var-{var.group_id}={var.id}")
    if top:
        parameters.append(f'top={top}')
    parameters.append("embed=players")
    parameters = '&'.join(parameters)
    data = make_request(
        f"https://www.speedrun.com/api/v1/leaderboards/{category.game_id}/category/{category.id}?{parameters}")
    if 'data' not in data:
        return
    return Leaderboard(data['data']['runs'], data['data']['players']['data'])


class Leaderboard:

    def __init__(self, run_data, players_data):
        self.runs = run_data
        self.players = players_data

    def get_run(self, rank=1):
        for run in self.runs:
            if run['place'] == rank:
                return Run(rank=run['place'],
                           player=self.lookup_user_name(run['run']['players'][0]['id']),
                           time=seconds_to_hhmmss(run['run']['times']['primary_t'])
                           )

    def get_pb(self, user_name):
        user_id = self.lookup_user_id(user_name)
        if not user_id:
            return
        for run in self.runs:
            if run['run']['players'][0]['rel'] == 'user' and run['run']['players'][0]['id'] == user_id:
                return Run(
                    rank=run['place'],
                    player=user_name,
                    time=seconds_to_hhmmss(run['run']['times']['primary_t'])
                )

    def lookup_user_name(self, id):
        for player in self.players:
            if player['id'] == id:
                return player['names']['international']

    def lookup_user_id(self, name):
        for player in self.players:
            if player['rel'] == 'user' and player['names']['international'].lower() == name.lower():
                return player['id']


@dataclass
class Run:
    rank: int
    player: str
    time: str
