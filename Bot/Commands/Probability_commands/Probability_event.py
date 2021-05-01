from Bot.Manage_settings.File_manager_factory import get_probabilities_settings_manager

DELIMITER = ';'

# abstract
class Probability_event:

    def __init__(self, name):
        self.name = name
        self.file_manager = get_probabilities_settings_manager()

    def respond(self, args, sender, channel_name):
        probability_setting = self.file_manager.get_setting(channel_name.lower())
        if not probability_setting:
            success = self.file_manager.add_new_setting(channel_name)
            if not success:
                return f"Error while trying to save new {self.name} data for {channel_name}"
            probability_setting = self.file_manager.get_setting(channel_name.lower())

        if len(args) == 0:
            return self.report_outcomes(probability_setting)
        if args[0].lower() in ['del', 'delete', 'remove', 'undo']:
            return self.remove_outcome(probability_setting, sender)
        return self.add_outcome(probability_setting, args[0].lower())

    def add_outcome(self, setting, outcome):
        outcome.replace(DELIMITER, '')
        if not self.is_valid(outcome):
            return self.invalid_outcome_message(outcome)
        print(setting.outcomes)

        if setting.outcomes == '':
            setting.outcomes = outcome
        else:
            setting.outcomes += f"{DELIMITER}{outcome}"

        success = self.file_manager.update_setting(setting)
        if success:
            return f"Added {self.name} outcome '{outcome}'"
        else:
            return f"Could not add {self.name} outcome '{outcome}'!"

    def remove_outcome(self, setting, sender):
        if sender.lower() != setting.name.lower():
            return "Only the channel owner is allowed to use this command"
        outcomes = setting.outcomes.split(DELIMITER)
        if len(outcomes) == 1 and outcomes[0] == '':
            return f"No {self.name} outcomes yet"
        to_remove = outcomes[-1]
        setting.outcomes = DELIMITER.join(outcomes[:-1])
        success = self.file_manager.update_setting(setting)
        if success:
            return f"Removed most recent {self.name} outcome '{to_remove}'"
        else:
            return f"Could not remove most recent {self.name} outcome!"

    def report_outcomes(self, setting):
        outcomes = setting.outcomes.split(DELIMITER)
        return self.outcome_stats(outcomes)


    # abstract
    def outcome_stats(self, outcomes):
        raise NotImplementedError('Subclasses of Probability_object must implement outcome_stats()')

    # abstract
    def is_valid(self, outcome):
        raise NotImplementedError('Subclasses of Probability_object must implement validate_result()')

    # abstract
    def invalid_outcome_message(self, outcome):
        raise NotImplementedError('Subclasses of Probability_object must implement invalid_outcome_message()')



class Dampe_event(Probability_event):

    def __init__(self, name):
        super().__init__(name)

    def outcome_stats(self, outcomes):
        return f"The outcomes are {outcomes}!"

    def is_valid(self, outcome):
        return outcome.isdigit() and int(outcome) > 0 and int(outcome) <= 9999

    def invalid_outcome_message(self, outcome):
        return f"{self.name} outcome '{outcome}' is invalid. Please supply an integer greater than zero."





