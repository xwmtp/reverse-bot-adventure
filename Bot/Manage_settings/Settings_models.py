from dataclasses import dataclass


@dataclass
class Setting:
    name: str

    def to_line(self, delimiter):
        return f"{delimiter}".join(self.__dict__.values())


@dataclass
class Channel_setting(Setting):
    src_name: str = ''
    racetime_name: str = ''


# outcome names have to match probability_event names
@dataclass
class Probabilities_setting(Setting):
    dampe: str = ''
    rock: str = ''
    truth_spinner: str = ''
    bush_patch: str = ''
