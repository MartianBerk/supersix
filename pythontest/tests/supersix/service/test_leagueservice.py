from unittest import TestCase, main
from unittest.mock import Mock, patch

from baked.lib.supersix.service.league_service import LeagueService


class LeagueServiceTests(TestCase):

    def setUp(self):
        self.mocked_db = Mock()
        self.mocked_db.get_columns.return_value = ["team", "points", "goal_difference"]

        self.mock_self = Mock(_db=self.mocked_db)

    @patch(f"{LeagueService.__module__}.LeagueTable")
    def test_league_table(self, mock_league_table):
        mock_league_table.side_effect = lambda **d: d  # return dict as constructor would receive

        self.mocked_db.get.return_value = [
            {"team": "Manchester Utd.", "points": 10, "goal_difference": 5, "goals_for": 8},
            {"team": "Liverpool", "points": 10, "goal_difference": 5, "goals_for": 8},
            {"team": "Manchester City", "points": 8, "goal_difference": 3, "goals_for": 5},
            {"team": "Chelsea", "points": 5, "goal_difference": 10, "goals_for": 10}
        ]

        league_table = LeagueService.league_table(self.mock_self, "season", "league")

        self.assertEqual(league_table,
                         [
                             {"position": "T1", "team": "Manchester Utd.", "points": 10, "goal_difference": 5, "goals_for": 8},
                             {"position": "T1", "team": "Liverpool", "points": 10, "goal_difference": 5, "goals_for": 8},
                             {"position": "3", "team": "Manchester City", "points": 8, "goal_difference": 3, "goals_for": 5},
                             {"position": "4", "team": "Chelsea", "points": 5, "goal_difference": 10, "goals_for": 10}
                         ])


if __name__ == '__main__':
    main()
