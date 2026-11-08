from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.domain.entities.coupon import Coupon


class CouponRepository(ABC):
    @abstractmethod
    def create(self, coupon: Coupon) -> Coupon: ...

    @abstractmethod
    def get_by_id(self, coupon_id: int) -> Optional[Coupon]: ...

    @abstractmethod
    def list_all(self, page: int, page_size: int) -> Tuple[List[Coupon], int]: ...

    @abstractmethod
    def update(self, coupon_id: int, coupon: Coupon) -> Optional[Coupon]: ...

    @abstractmethod
    def deactivate(self, coupon_id: int) -> bool: ...