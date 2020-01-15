from datetime import datetime, timedelta

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command




class TimerApp(AppConfig):
	end_time = None
	time_left = None
	time_at_start = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)

		await self.instance.permission_manager.register(
			'timer',
			'Custom timer commands for admins',
			app=self,
			min_level=2
		)

		await self.instance.command_manager.register(
			Command(
				command='set',
				namespace='timer',
				target=self.set_timer,
				admin=True
			).add_param(name='seconds', type=int, required=True),
			Command(
				command='add',
				namespace='timer',
				target=self.increment_timer,
				admin=True
			).add_param(name='seconds', type=int, required=True),
			Command(
				command='sub',
				namespace='timer',
				target=self.decrement_timer,
				admin=True
			).add_param(name='seconds', type=int, required=True),
			Command(
				command='stop',
				namespace='timer',
				target=self.stop_timer,
				admin=True
			)
		)

	async def map_start(self, map, restarted, **kwargs):
		self.time_at_start = datetime.now()



	async def set_timer(self, player, data, *args, **kwargs):
		try:
			seconds = abs(int(data.seconds))


		except ValueError:
			# TODO: Send error message
			return

		now = datetime.now()

		time_since_start = int((now - self.time_at_start).total_seconds())

		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': time_since_start + seconds}
		)

		now = datetime.now()

		self.end_time = now + timedelta(seconds=seconds)
		self.time_left = self.end_time - now

		message = f'$z$s{player.nickname}$z$s has started a new timer!'

		await self.instance.chat(message)

	async def increment_timer(self, player, data, *args, **kwargs):
		try:
			seconds = int(data.seconds)

		except ValueError:
			# TODO: Send error message

			return

		self.end_time += timedelta(seconds=seconds)
		self.time_left += timedelta(seconds=seconds)

		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': self.time_left.seconds}
		)

		message = f'$z$s{player.nickname}$z$s has increased the timer with {data.seconds} seconds!'

		await self.instance.chat(message)


	async def decrement_timer(self, player, data, *args, **kwargs):
		try:
			seconds = int(data.seconds)

		except ValueError:
			# TODO: Send error message
			return

		self.end_time -= timedelta(seconds=seconds)
		time_left = self.time_left - timedelta(seconds=seconds)

		if time_left.seconds <= 0 or time_left.seconds >= self.time_left.seconds:
			message = f'You cannot set a decrease the timer by that much, use //timer stop to stop the current timer instead'

			await self.instance.chat(message, player.login)
			return
		self.time_left = time_left

		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': self.time_left.seconds}
		)
		message = f'$z$s{player.nickname}$z$s has decreased the timer with {data.seconds} seconds!'

		await self.instance.chat(message)

	async def stop_timer(self, player, data, *args, **kwargs):
		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': 0}
		)

		message = f'$z$s{player.nickname}$z$s has stopped the timer!'
		await self.instance.chat(message)
