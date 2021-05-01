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


@dataclass
class Probabilities_setting(Setting):
    outcomes: str = ''