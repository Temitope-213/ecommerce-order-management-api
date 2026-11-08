from abc import ABC, abstractmethod

from app.domain.entities.system_info import SystemInfo


class StatsRepository(ABC):
    @abstractmethod
    def get_system_info(self) -> SystemInfo: ...