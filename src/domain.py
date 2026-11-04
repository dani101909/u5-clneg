from dataclasses import dataclass

VIP_DISCOUNT_RATE = 0.15


class CustomerHasDebt(Exception):
    pass


@dataclass
class Order:
    total: float
    vip: bool = False
    status: str = "NEW"
    discount: float = 0.0

    def confirm(self, customer_debt=0):
        self._validate_can_confirm(customer_debt)
        self.discount = self._calculate_discount()
        self.status = "CONFIRMED"
        return self.total - self.discount

    def _validate_can_confirm(self, customer_debt):
        if self.status == "CONFIRMED":
            raise ValueError("already confirmed")
        if self.total <= 0:
            raise ValueError("total must be positive")
        if customer_debt > 0:
            raise CustomerHasDebt("outstanding debt")

    def _calculate_discount(self):
        return round(self.total * VIP_DISCOUNT_RATE, 2) if self.vip else 0.0