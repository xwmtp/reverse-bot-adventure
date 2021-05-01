import logging

class File_manager:

    def __init__(self, setting_class, file_path, delimiter='#'):
        self.setting_class = setting_class
        self.file_path = file_path
        self.delimiter = delimiter

    def read_settings(self):
        with open(self.file_path, 'r') as file:
            lines = file.read().splitlines()

        settings = []
        for line in lines:
            try:
                fields = line.split(self.delimiter)
                settings.append(self.setting_class(*fields))
            except ValueError:
                logging.warning(f"Could not parse setting {line} from {self.file_path}")
                continue
        return settings

    def get_setting(self, name):
        settings = self.read_settings()
        for setting in settings:
            if setting.name.lower() == name.lower():
                return setting

    def remove_setting(self, name):
        settings = self.read_settings()
        new_settings = []
        for setting in settings:
            if setting.name.lower() != name.lower():
                new_settings.append(setting)
        success = self.overwrite_settings(new_settings)
        return success

    def update_setting(self, new_setting):
        settings = self.read_settings()
        new_settings = []
        for setting in settings:
            if setting.name.lower() == new_setting.name.lower():
                new_settings.append(new_setting)
            else:
                new_settings.append(setting)
        success = self.overwrite_settings(new_settings)
        return success

    def overwrite_settings(self, new_settings):
        try:
            with open(self.file_path, 'w') as file:
                file.write('\n'.join([s.to_line(self.delimiter) for s in new_settings]) + '\n')
            return True
        except Exception as e:
            logging.error(f"Error while overwriting settings in {self.file_path}: {repr(e)}")
            return False

    def add_new_setting(self, name):
        new_setting = self.setting_class(name)
        try:
            with open(self.file_path, 'a') as file:
                file.write(new_setting.to_line(self.delimiter) + '\n')
            return True
        except Exception as e:
            logging.error(f"Error while adding setting {new_setting} to {self.file_path}. Error: {repr(e)}")
            return False
