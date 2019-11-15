
from pyplanet.apps.contrib.help.views import CommandsListView
from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command



class HelpApp(AppConfig):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_init(self):
		help_description = 'Shows list of all commands, /help [command] for help per command'
		admin_help_description = 'Shows list of all admin commands, //help [command] for help per command'
		await self.instance.command_manager.register(
			Command(
				command='help',
				target=self.help,
				admin=False,
				description=help_description
			).add_param('command', nargs='*', required=False),
			Command(
				command='help',
				target=self.help,
				admin=True,
				description=admin_help_description
			).add_param('command', nargs='*', required=False)
		)



	async def help(self, player, command, data, **kwargs):
		help_command = command
		filter_admin = bool(help_command.admin)
		if data.command:
			cmd_args = data.command

			# HACK: Add / before an admin command to match the right command.
			if filter_admin and cmd_args:
				cmd_args[0] = '/{}'.format(cmd_args[0])

			# Find the right command.
			cmd_instance = None
			for cmd in self.instance.command_manager._commands:
				if cmd.match(cmd_args):
					cmd_instance = cmd
					break
			# If found, show the usage of the command.
			if cmd_instance:
				await self.instance.chat(
					'$z$s{}'.format(cmd_instance.usage_text),
					player
				)
				return

		commands = [c for c in self.instance.command_manager._commands if c.admin is filter_admin]
		view = CommandsListView(self, commands)
		await view.display(player=player.login)
