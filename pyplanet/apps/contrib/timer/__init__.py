from datetime import datetime, timedelta

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command




class TimerApp(AppConfig):
	original_timer = None
	timer_set = False
	timer_active = False
	current_script = None
	current_timer = None

	end_time = None
	time_left = None
	time_at_start = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)
		self.context.signals.listen(mp_signals.map.map_end, self.map_end)

		self.original_timer = None
		self.timer_set = False
		self.timer_active = False
		self.current_timer = None

		self.end_time = None
		self.time_left = None
		self.time_at_start = None
		self.current_script = await self.instance.mode_manager.get_current_script()


		await self.instance.permission_manager.register(
			'timer',
			'Custom timer commands for admins',
			app=self,
			min_level=2
		)

		set_description = 'Set a timer for current map in X minutes'
		add_description = 'Add X minutes to current timer'
		sub_description = 'Subtract X minutes from current timer'
		stop_description = 'Stop current timer (remove timer from current map)'
		update_description = 'Makes X the default timelimit for the server'

		await self.instance.command_manager.register(
			Command(
				command='set',
				namespace='timer',
				target=self.set_timer,
				admin=True,
				description=set_description
			).add_param(name='minutes', type=int, required=True),
			Command(
				command='add',
				namespace='timer',
				target=self.increment_timer,
				admin=True,
				description=add_description
			).add_param(name='minutes', type=int, required=True),
			Command(
				command='sub',
				namespace='timer',
				target=self.decrement_timer,
				admin=True,
				description=sub_description
			).add_param(name='minutes', type=int, required=True),
			Command(
				command='stop',
				namespace='timer',
				target=self.stop_timer,
				admin=True,
				description=stop_description
			),
			Command(
				command='update',
				namespace='timer',
				target=self.update_timer,
				admin=True,
				description=update_description
			).add_param(name='minutes', type=int, required=True)
		)

	async def map_start(self, map, restarted, **kwargs):
		if restarted:
			await self.map_end(map)
		self.time_at_start = datetime.now()

	async def map_end(self, map, **kwargs):
		if self.timer_set:
			await self.instance.mode_manager.update_settings(
				{'S_TimeLimit': self.original_timer if self.original_timer is not None else 300}
			)

	async def set_timer(self, player, data, *args, **kwargs):

		if self.current_script != 'TimeAttack':
			message = f'$z$sWe need to be in timeattack!'

			await self.instance.chat(message)
			return

		try:
			seconds = abs(int(data.minutes)) * 60


		except ValueError:
			# TODO: Send error message
			return


		now = datetime.now()
		if not self.timer_set:

			self.timer_set = True

			self.original_timer = await (self.instance.mode_manager.get_settings())
			self.original_timer = self.original_timer['S_TimeLimit']

		if not self.timer_active:
			self.timer_active = True

		# You have to subtract 3 here to account for map start being 3 seconds
		# before you can acutally start playing

		self.current_timer = seconds

		time_since_start = int((now - self.time_at_start).total_seconds()) - 3

		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': time_since_start + seconds}
		)

		now = datetime.now()

		self.end_time = now + timedelta(seconds=seconds)
		self.time_left = self.end_time - now

		message = f'$z$s{player.nickname}$z$s has started a new timer for $z$s$fff{data.minutes}$z$s minutes!'

		await self.instance.chat(message)

	async def increment_timer(self, player, data, *args, **kwargs):
		try:
			seconds = abs(int(data.minutes)) * 60

		except ValueError:
			# TODO: Send error message

			return

		if not self.timer_active:
			message = f'$z$sThere is currently no timer running!'

			await self.instance.chat(message)
			return

		self.end_time += timedelta(seconds=seconds)
		self.time_left += timedelta(seconds=seconds)

		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': self.time_left.seconds}
		)

		message = f'$z$s{player.nickname}$z$s has increased the timer with $z$s$fff{data.minutes}$z$s minutes!'

		await self.instance.chat(message)


	async def decrement_timer(self, player, data, *args, **kwargs):
		try:
			seconds = abs(int(data.minutes)) * 60

		except ValueError:
			# TODO: Send error message
			return

		if not self.timer_active:
			message = f'$z$sThere is currently no timer running!'

			await self.instance.chat(message)
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
		message = f'$z$s{player.nickname}$z$s has decreased the timer with $z$s$fff{data.minutes}$z$s minutes!'

		await self.instance.chat(message)

	async def stop_timer(self, player, data, *args, **kwargs):
		await self.instance.mode_manager.update_settings(
			{'S_TimeLimit': 0}
		)

		message = f'$z$s{player.nickname}$z$s has stopped the timer!'
		await self.instance.chat(message)
		self.timer_active = False

	async def update_timer(self, player, data, *args, **kwargs):
		try:

			self.original_timer = int(data.minutes) * 60
		except ValueError:
			return

		message = f'$z$s{player.nickname}$z$s updated the default timer to $z$s$fff{data.minutes}$z$s minutes!'

		await self.instance.chat(message)
