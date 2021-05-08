from Bot.Manage_settings.File_manager_factory import get_probabilities_settings_manager
from Bot.Utils import make_request
from scipy import stats
import math
import time

DELIMITER = ';'

# abstract
class Probability_event:

    def __init__(self, name, display_name = '', cooldown_seconds=10):
        self.name = name
        self.cooldown_seconds = cooldown_seconds
        if display_name == '':
            self.display_name = self.name
        else:
            self.display_name = display_name
        self.file_manager = get_probabilities_settings_manager()
        self.cooldowns = {}

    def respond(self, args, sender, channel_name):
        probability_setting = self.file_manager.get_setting(channel_name.lower())
        if not probability_setting:
            success = self.file_manager.add_new_setting(channel_name)
            if not success:
                return f"Error while trying to save new {self.display_name} data for {channel_name}"
            probability_setting = self.file_manager.get_setting(channel_name.lower())
        if len(args) == 0:
            return self.report_outcomes(probability_setting)
        if args[0].lower() in ['clear_all']:
            return self.reset_all(probability_setting, sender)
        if args[0].lower() in ['del', 'delete', 'remove', 'undo']:
            return self.remove_outcome(probability_setting, sender)
        return self.add_outcome(probability_setting, args[0].lower(), sender)

    def add_outcome(self, setting, outcome, sender):
        if sender.lower() != setting.name.lower() and not is_live(setting.name.lower()):
            return "Only the channel owner can add outcomes when the stream is not live"

        if self.cooldown_active(setting.name.lower()):
            return f"Cooldown of {self.cooldown_seconds}s is active."

        transformed_outcome = self.transform(outcome)
        if not self.is_valid(transformed_outcome):
            return self.invalid_outcome_message(outcome)
        outcome = transformed_outcome

        outcomes = self.get_outcomes(setting)
        if outcomes == '':
            self.set_outcomes(setting, outcome)
        else:
            self.set_outcomes(setting, outcomes + f"{DELIMITER}{outcome}")

        success = self.file_manager.update_setting(setting)
        if success:
            self.cooldowns[setting.name.lower()] = time.time()
            return f"Added {self.display_name} outcome '{outcome}'" + self.outcome_odds(outcome)
        else:
            return f"Could not add {self.display_name} outcome '{outcome}'!"

    def remove_outcome(self, setting, sender):
        if sender.lower() != setting.name.lower():
            return "Only the channel owner is allowed to use this command"
        outcomes = self.get_outcomes(setting).split(DELIMITER)
        if len(outcomes) == 1 and outcomes[0] == '':
            return f"No {self.display_name} outcomes yet"
        to_remove = outcomes[-1]
        self.set_outcomes(setting, DELIMITER.join(outcomes[:-1]))
        success = self.file_manager.update_setting(setting)
        if success:
            return f"Removed most recent {self.display_name} outcome '{to_remove}'"
        else:
            return f"Could not remove most recent {self.display_name} outcome!"

    def reset_all(self, setting, sender):
        if sender.lower() != setting.name.lower():
            return "Only the channel owner is allowed to use this command"
        self.set_outcomes(setting, '')
        success = self.file_manager.update_setting(setting)
        if success:
            return f"Successfully removed all the saved {self.display_name} outcomes"
        else:
            return f"Could not reset the {self.display_name} outcomes!"

    def report_outcomes(self, setting):
        outcomes = self.get_outcomes(setting).split(DELIMITER)
        if len(outcomes) == 1 and outcomes[0] == '':
            return f"No {self.display_name} outcomes have been recorded yet."
        return self.outcome_stats(outcomes, setting.name)

    def cooldown_active(self, channel_name):
        if channel_name not in self.cooldowns:
            return
        last_call = self.cooldowns[channel_name]
        return time.time() - last_call < self.cooldown_seconds

    def get_outcomes(self, setting):
        return getattr(setting, self.name.lower())

    def set_outcomes(self, setting, outcomes):
        setattr(setting, self.name.lower(), outcomes)

    # override
    def transform(self, outcome):
        return outcome.replace(DELIMITER, '').lower()

    def outcome_odds(self, outcome):
        return ''

    # abstract
    def outcome_stats(self, outcomes, channel_name):
        raise NotImplementedError('Subclasses of Probability_object must implement outcome_stats()')

    # abstract
    def is_valid(self, outcome):
        raise NotImplementedError('Subclasses of Probability_object must implement validate_result()')

    # abstract
    def invalid_outcome_message(self, outcome):
        raise NotImplementedError('Subclasses of Probability_object must implement invalid_outcome_message()')



class Dampe_event(Probability_event):

    def __init__(self):
        super().__init__('Dampe')

    def outcome_stats(self, outcomes, channel_name):
        outcomes_ints = [int(outcome) for outcome in outcomes]
        average_tries = sum(outcomes_ints)/len(outcomes_ints)
        string = f"Out of {len(outcomes_ints)} Dampe visits, {channel_name} needed {round(average_tries,1)} tries on average."
        if average_tries == 10:
            string += " This is exactly what is expected!"
        if average_tries < 10:
            string += f" This is better than the expected average of 10 tries."
        if average_tries > 10:
            string += f" This is worse than the expected average of 10 tries."
        length = 20 if len(outcomes_ints) >= 20 else len(outcomes_ints)
        string += f" Tries needed for the last {length} Dampe visits: {', '.join(reversed(outcomes[-20:]))}"
        return string

    def outcome_odds(self, outcome):
        outcome = int(outcome)
        tries = "try" if outcome == 1 else "tries"
        decimals = 3 if outcome < 50 else 5
        if outcome == 1:
            return f' (chances of getting {outcome}st {tries}: 10%)'
        if outcome <= 6:
            return f' (chances of needing {outcome} {tries} or less: {round((1-(0.9**outcome))*100,decimals)}%)'
        else:
            return f' (chances of needing {outcome} {tries} or more: {round((1-(1 - (0.9 ** outcome)))*100,decimals)}%)'

    def is_valid(self, outcome):
        return outcome.isdigit() and int(outcome) > 0 and int(outcome) <= 9999

    def invalid_outcome_message(self, outcome):
        return f"{self.display_name} outcome '{outcome}' is invalid. Please supply an integer greater than zero."


class Rock_event(Probability_event):

    def __init__(self):
        super().__init__('rock', cooldown_seconds=5)

    def outcome_stats(self, outcomes, channel_name,):
        successes = outcomes.count('yes')
        failures = outcomes.count('no')
        total = successes + failures
        drops = "drop" if successes == 1 else "drops"
        rocks = "rock" if total == 1 else "rocks"
        string = f"{channel_name} got {successes} bomb {drops} out of {total} {rocks}."
        bomb_chance = 1 / 16
        ratio = successes / total
        if ratio == 1 / 16:
            string += f" That's a ratio of {round(ratio,3)}, which is exactly equal to the expected {bomb_chance} (1/16)."
            string += f" The chances of getting exactly {successes} {drops} out of {total} {rocks} are {round(stats.binom.pmf(successes,total,1/16)*100,3)}%."
        if ratio < 1 / 16:
            string += f" That's a ratio of {round(ratio, 3)}, which is less than the expected {bomb_chance} (1/16)."
            string += f" The chances of getting {successes} {drops} or less out of {total} {rocks} are {round(stats.binom.cdf(successes,total,1/16)*100,3)}%."
        else:
            string += f" That's a ratio of {round(ratio, 3)}, which is more than the expected {bomb_chance} (1/16)."
            string += f" The chances of getting {successes} {drops} or more out of {total} {rocks} are {round((1 - stats.binom.cdf(successes-1,total,1/16))*100,3)}%."

        return string

    def outcome_odds(self, outcome):
        if outcome == 'yes':
            return " (odds 1/16)"
        if outcome == 'no':
            return " (odds 15/16)"

    def is_valid(self, outcome):
        return outcome in ['yes', 'no']

    def invalid_outcome_message(self, outcome):
        return f"'{outcome}' is not a valid {self.display_name} outcome, please supply 'yes' or 'no'"

    def transform(self, outcome):
        outcome = outcome.replace(DELIMITER, '').lower()
        if outcome.lower() in ['yes', '1', 'y', 'true', 'bomb']:
            return 'yes'
        if outcome.lower() in ['no', '0', 'n', 'false', 'nothing', 'none']:
            return 'no'
        else:
            return outcome


class Spinner_event(Probability_event):

    def __init__(self):
        super().__init__('truth_spinner', 'truth spinner', 20)

    def outcome_stats(self, outcomes, channel_name):
        outcomes_ints = [int(outcome) for outcome in outcomes]
        average_tries = sum(outcomes_ints)/len(outcomes_ints)
        string = f"Out of {len(outcomes_ints)} truth spinners, {channel_name} needed {round(average_tries,2)} tries on average."
        if average_tries == 17 / 9:
            string += " This is exactly what is expected!"
        if average_tries < 17 / 9:
            string += f" This is better than the expected average of 1.89 tries."
        if average_tries > 17 / 9:
            string += f" This is worse than the expected average of 1.89 tries."
        length = 20 if len(outcomes_ints) >= 20 else len(outcomes_ints)
        string += f" Tries needed for the last {length} truth spinners: {', '.join(reversed(outcomes[-20:]))}"
        return string

    def outcome_odds(self, outcome):
        if outcome == '1':
            return " (odds 4/9)"
        if outcome == '2':
            return " (odds 2/9)"
        if outcome == '3':
            return " (odds 1/3)"

    def is_valid(self, outcome):
        return outcome in ['1', '2', '3']

    def invalid_outcome_message(self, outcome):
        return f"'{outcome}' is not a valid {self.display_name} outcome, please use a number between 1 and 3."

    def transform(self, outcome):
        outcome = outcome.replace(DELIMITER, '').lower()
        if outcome.lower() in ['1', '1st', 'first', '1st try', 'first try']:
            return '1'
        if outcome.lower() in ['2', '2nd', 'second', '2nd try', 'second try']:
            return '2'
        if outcome.lower() in ['3', '3rd', 'third', '3rd try', 'third try']:
            return '3'
        else:
            return outcome



class Bush_event(Probability_event):

    def __init__(self):
        super().__init__('bush_patch', 'bush patch', 5)

    def outcome_stats(self, outcomes, channel_name):
        outcomes_ints = [int(outcome) for outcome in outcomes]
        average_drops = sum(outcomes_ints)/len(outcomes_ints)
        string = f"Out of {len(outcomes_ints)} bush patches, {channel_name} got {round(average_drops,1)} bomb drops on average."
        if average_drops == 0.75:
            string += " This is exactly what is expected!"
        if average_drops < 10:
            string += f" This is better than the expected average of 0.75 drops."
        if average_drops > 10:
            string += f" This is worse than the expected average of 0.75 drops."
        length = 20 if len(outcomes_ints) >= 20 else len(outcomes_ints)
        string += f" Number of bomb drops in the last {length} bush patches: {', '.join(reversed(outcomes[-20:]))}"
        return string

    def outcome_odds(self, outcome):
        outcome = int(outcome)
        drops = "drop" if outcome == 1 else "drops"
        if outcome > 0:
            extra_string = f", chance of getting {outcome} bomb {drops} or more: {custom_round((1 - stats.binom.cdf(outcome-1,12,1/16))*100)}%"
        else:
            extra_string = ''
        return f" (chance of getting exactly {outcome} bomb {drops}: {custom_round(stats.binom.pmf(outcome,12,1/16)*100)}%{extra_string})"


    def is_valid(self, outcome):
        return outcome.isdigit() and int(outcome) >= 0 and int(outcome) <= 12

    def invalid_outcome_message(self, outcome):
        return f"{self.display_name} outcome '{outcome}' is invalid. Please supply an integer between 0 and 12."




def custom_round(number, decimals=2):
    if number > 1:
        return round(number, decimals)
    dist = int(math.log10(abs(number)))
    return round(number, abs(dist) + decimals)

def is_live(channel):
    uptime = make_request(f"https://decapi.me/twitch/uptime/{channel}", text_only=True)
    return 'offline' not in uptime

