from abc import ABCMeta, abstractmethod


class AbstractConnector(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def collect_leagues(cls):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def collect_matches(cls, league, matchday=None, look_ahead=3):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def collect_historical_scores(cls, league, matchday):
        raise NotImplementedError()

    @classmethod
    def collect_scores(cls, league, matchday):
        raise NotImplementedError()
