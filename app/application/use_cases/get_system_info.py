from app.domain.entities.system_info import SystemInfo
from app.domain.repositories.stats_repository import StatsRepository


class GetSystemInfo:
    def __init__(self, stats: StatsRepository):
        self.stats = stats

    def execute(self) -> SystemInfo:
        return self.stats.get_system_info()