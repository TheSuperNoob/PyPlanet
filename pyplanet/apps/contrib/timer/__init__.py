from datetime import datetime, timedelta

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command


class TimerApp(AppConfig):
	start_time = None
	end_time = None
	time_left = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
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

	async def set_timer(self, player, data, *args, **kwargs):

		try:
			milliseconds = int(data.seconds) * 1000
			self.start_time = datetime.now()
			self.end_time = start_time + delta(milliseconds=milliseconds)

		except ValueError:
			# TODO: Send error message
			return

		await self.instance.mode_manager.update_settings(
			{'TimeAttackLimit': milliseconds}
		)

		message = f'$z$s{player.nickname}$z$s has started a new timer!'

		await self.instance.chat(message)

	async def increment_timer(self, player, data, *args, **kwargs):
		try:
			milliseconds = int(data.seconds) * 1000

		except ValueError:
			# TODO: Send error message

			return

		await self.instance.mode_manager.update_settings(
			{'TimeAttackLimit': self.get_time_left() + milliseconds}
		)

		message = f'$z$s{player.nickname}$z$s has increased the timer with {data.seconds} seconds!'

		await self.instance.chat(message)


	async def decrement_timer(self, player, data, *args, **kwargs):
		try:
			milliseconds = int(data.seconds) * 1000

		except ValueError:
			# TODO: Send error message
			return

		time_left = self.get_time_left() - milliseconds

		if time_left <= 0:
			message = f'You cannot set a decrease the timer by that much, use //timer stop to stop the current timer instead'

			await self.instance.chat(message, player.login)
			return

		await self.instance.mode_manager.update_settings(
			{'TimeAttackLimit': time_left}
		)
		message = f'$z$s{player.nickname}$z$s has decreased the timer with {data.seconds} seconds!'

		await self.instance.chat(message)

	async def stop_timer(self, player, data, *args, **kwargs):
		await self.instance.mode_manager.update_settings(
			{'TimeAttackLimit': 0}
		)

		message = f'$z$s{player.nickname}$z$s has stopped the timer!'
		await self.instance.chat(message)

	def get_time_left():
		# TODO: Add a limit to this. We don't want anyone adding a timer that is
		# days long. Perhaps: 8 hours max? (Give this in milliseconds)

		# TODO: is there a better way to do this? Perhaps datetime has an
		# automatic conversion (Research)
		self.time_left = self.end_time - datetime.now()
		hours_to_milli = int(self.time_left.hours * 3.6e+6) if self.time_left.hours else 0
		minutes_to_milli = self.time_left.minutes * 60000 if self.time_left.minutes else 0
		seconds_to_milli = self.time_left.minutes * 1000 if self.time_left.seconds else 0
		micro_to_milli = self.time_left.microseconds * 100 if self.time_left.microseconds else 0

		time_in_milliseconds = (
			hours_to_milli +
			minutes_to_milli +
			seconds_to_milli +
			micro_to_milli
		)

		return time_in_milliseconds
