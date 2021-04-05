# Reverse Bot Adventure

Twitch chatbot for Ocarina of Time speedrunners. It can retrieve world records and personal bests from Speedrun.com and get information on your current Racetime.gg race.

## Adding the bot to your channel
Head to [twitch.tv/ReverseBotAdventure](https://twitch.tv/ReverseBotAdventure) and use one of the following commands in chat:

* `!add` to invite the bot to your channel.
* `!remove` to remove the bot from your channel.
* `!setsrc` to set your Speedrun.com user name. Only necessary when it differs from your Twitch user name.
* `!setracetime` to set your Racetime.gg user name. Only necessary when it differs from your Twitch user name.
* `!help` to see which commands you can use.
* `!ping` to check if the bot is currently online.

Don't forget to mod the bot in your channel after adding it so it can send quick responses.

## Commands for your Twitch channel
Note that this bot was created for Ocarina of Time speedrunning, so the commands will only work for OoT categories (main and extensions) and races.

If you use one of the Racetime commands at least once before the race finishes, you can still see information up to one hour after the race is completed (unless you join a new race within that time).

### Speedrun.com
* `!wr` to retrieve the current world record for a category. If you use it without argument, the bot will try to find a category in your current stream title. If you want to look for a specific category, provide an argument (e.g. !wr all dungeons no srm).
* `!pb` to retrieve the personal best of the streamer. Arguments work the same as for the wr command.
* `!src` to get a link to the leaderboard page on Speedrun.com. Arguments work the same as for the wr command.

### Racetime.gg
* `!race` to get the current race the streamer is active in. Returns the race category, the url and the entrants. Updates with finish times when people finish.
* `!goal` to get the goal ('race info') of the current race.
* `!entrants` to only print the entrants in the race (and their finish times after they finish).

### Help
* `!help` to see the commands and additional help information.
* `!commands` to just see the commands you can use.
