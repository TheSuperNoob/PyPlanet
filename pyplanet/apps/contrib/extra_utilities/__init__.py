from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command



class ExtraUtilitiesApp(AppConfig):
	name = 'pyplanet.apps.contrib.extra_utilities'
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='afk', target=self.afk),
			Command(command='hello', aliases=['hi'], target=self.hello),
		)


	async def afk(self, player, data, **kwargs):
		message = f'$z$s$ff0[{player.nickname}$z$s$ff0] $iAway from keyboard!'

		await self.instance.gbx.multicall(
			self.instance.gbx('ForceSpectator', player.login, 3),
			self.instance.chat(message, raw=True)
			)

	async def hello(self, player, data, **kwargs):

		message = f'$z$s$ff0[{player.nickname} $z$s$ff0] $iHello all!'

		await self.instance.chat(message, raw=True)
