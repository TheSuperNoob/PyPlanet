from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.apps.core.statistics.models import Score
from pyplanet.utils import times
from pyplanet.views.generics.list import ManualListView


class StatsScoresListView(ManualListView):
	title = 'Personal time progression on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player):
		"""
		Init score list view.

		:param player: Player instance.
		:param app: App instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		super().__init__(self)

		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False

	async def get_data(self):
		score_list = await Score.objects.execute(
			Score.select(Score, Player)
				.join(Player)
				.where(Score.map == self.app.instance.map_manager.current_map.get_id())
				.order_by(Score.created_at.asc())
		)

		scores_list = list(score_list)

		personal_list = [s for s in scores_list if s.player.id == self.player.get_id()]

		if len(personal_list) == 0:
			message = '$i$f00There are no personal scores available for $fff{}$z$s$f00$i!'.format(self.app.instance.map_manager.current_map.name)
			await self.app.instance.chat(message, self.player)
			return

		print([s for s in scores_list if s.player.id == self.player.get_id()])

		local_record = min([s.score for s in scores_list])

		scores = list()
		last_best = 0
		last_best_index = 1
		personal_best = min([s.score for s in personal_list])
		for score_in_list in personal_list:
			historical_local = min([s.score for s in scores_list if s.created_at <= score_in_list.created_at])

			score = dict()
			score['index'] = ''
			score['score'] = times.format_time(score_in_list.score)
			score['created_at'] = score_in_list.created_at.strftime('%d-%m-%Y %H:%M:%S')
			score['difference_to_pb'] = times.format_time((score_in_list.score - personal_best))
			score['difference_to_prev'] = ''
			score['difference_to_local'] = times.format_time((score_in_list.score - local_record))
			score['historical_local'] = times.format_time(historical_local)
			score['difference_to_hist_local'] = times.format_time((score_in_list.score - historical_local))

			if last_best == 0:
				score['index'] = last_best_index
				last_best = score_in_list.score
				last_best_index += 1
			elif score_in_list.score < last_best:
				score['index'] = last_best_index
				score['difference_to_prev'] = '$00f- {}'.format(times.format_time((last_best - score_in_list.score)))
				last_best = score_in_list.score
				last_best_index += 1
			else:
				score['difference_to_prev'] = '$f00+ {}'.format(times.format_time((score_in_list.score - last_best)))

			if score_in_list.score == local_record:
				score['difference_to_local'] = ''
			else:
				score['difference_to_local'] = '$f00+ {}'.format(score['difference_to_local'])

			if score_in_list.score == historical_local:
				score['difference_to_hist_local'] = ''
			else:
				score['difference_to_hist_local'] = '$f00+ {}'.format(score['difference_to_hist_local'])

			if score_in_list.score == personal_best:
				score['index'] = 'PB'
				score['difference_to_pb'] = ''
			else:
				score['difference_to_pb'] = '$f00+ {}'.format(score['difference_to_pb'])

			scores.append(score)

		return scores

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': False,
				'searching': False,
				'width': 6,
				'type': 'label'
			},
			{
				'name': 'Time',
				'index': 'score',
				'sorting': False,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
			{
				'name': 'From PB',
				'index': 'difference_to_pb',
				'sorting': False,
				'searching': False,
				'width': 28,
				'type': 'label'
			},
			{
				'name': 'From prev. PB',
				'index': 'difference_to_prev',
				'sorting': False,
				'searching': False,
				'width': 34,
				'type': 'label'
			},
			{
				'name': 'From Local',
				'index': 'difference_to_local',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'Hist. Local',
				'index': 'historical_local',
				'sorting': False,
				'searching': False,
				'width': 28,
				'type': 'label'
			},
			{
				'name': 'From hist. Local',
				'index': 'difference_to_hist_local',
				'sorting': False,
				'searching': False,
				'width': 34,
				'type': 'label'
			},
			{
				'name': 'Driven at',
				'index': 'created_at',
				'sorting': False,
				'searching': False,
				'width': 40,
				'type': 'label'
			},
		]
