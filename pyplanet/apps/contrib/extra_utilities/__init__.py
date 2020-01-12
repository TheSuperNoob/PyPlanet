from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.contrib.player.exceptions import PlayerNotFound



class ExtraUtilitiesApp(AppConfig):
	name = 'pyplanet.apps.contrib.extra_utilities'
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):

		await self.instance.permission_manager.register(
			'message', 'Send a message as server', app=self, min_level=3
		)

		await self.instance.permission_manager.register(
			'fakeplayer',
			'Send a fake message as a player',
			app=self,
			min_level=3
		)

		await self.instance.command_manager.register(
			Command(command='afk', target=self.afk),
			Command(command='hello', aliases=['hi'], target=self.hello),
			Command(
				command='message',
				aliases=['servermessage'],
				target=self.message,
				perms='extra_utilities:message',
				admin=True
			),
			Command(
				command='fakeplayer',
				target=self.fake_player,
				perms='extra_utilities:fakeplayer',
				admin=True
			).add_param(name='login', required=True),

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

	async def message(self, player, data, **kwargs):
		message = '$z$s$ff0[{} $z$s$ff0] {}'.format(self.instance.game.server_name, ' '.join(kwargs['raw']))

		await self.instance.chat(message, raw=True)


	async def fake_player(self, player, data, **kwargs):
		try:
			fake_player  = [p for p in self.instance.player_manager.online if p.login == data.login]
			if not fake_player:
				raise Exception()


		except Exception:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player.login)
			return

		message = '$z$ff0[{} $z$ff0] {}'.format(fake_player[0].nickname, ' '.join(kwargs['raw'][1:]))

		await self.instance.chat(message, raw=True)
