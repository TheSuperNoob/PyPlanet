from pyplanet.views.generics.list import ManualListView


class CommandsListView(ManualListView):
	title = 'All available commands'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	fields = [
		{
			'name': '#',
			'index': 'index',
			'sorting': True,
			'searching': False,
			'width': 10,
			'type': 'label'
		},
		{
			'name': 'Command',
			'index': 'command_name',
			'sorting': False,
			'searching': True,
			'width': 40
		},
		{
			'name': 'Description',
			'index': 'command_description',
			'sorting': False,
			'searching': False,
			'width': 100,
			'type': 'lable'
		},
		{
			'name': 'Usage',
			'index': 'command_usage',
			'sorting': False,
			'searching': False,
			'width': 40,
			'type': 'label'
		}
	]

	def __init__(self, app, commands):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.commands = commands

	async def get_data(self):
		commands = []
		for index, command in enumerate(self.commands, 1):
			commands.append({
				'index': index,
				'command_name': command,
				'command_description': command.description if command.description else '',
				'command_usage': command.usage_text
			})
		return commands
