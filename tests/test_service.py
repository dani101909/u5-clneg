from unittest.mock import Mock

import pytest

from src.application import OrderService
from src.domain import Order


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)

def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))

def test_gateway_rejected_vip_200():
    # Arrange: pasarela simulada que rechaza el pago; pedido VIP de 200
    gateway = Mock()
    gateway.charge.return_value = False
    service = OrderService(gateway)
    order = Order(200, vip=True)
    # Act + Assert: el servicio debe lanzar RuntimeError("payment rejected")
    with pytest.raises(RuntimeError, match="payment rejected"):
        service.checkout(order)
    # Assert: el intento de cobro fue por 170 (200 menos 15% de descuento)
    gateway.charge.assert_called_once_with(170)

def test_gateway_timeout():
    # Arrange: pasarela simulada que no responde a tiempo
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("gateway timeout")
    # Act + Assert: el servicio no oculta la falla, la deja pasar
    with pytest.raises(TimeoutError):
        OrderService(gateway).checkout(Order(100))
    gateway.charge.assert_called_once_with(100)

def test_known_risk_order_confirmed_even_if_payment_rejected():
    # RIESGO DOCUMENTADO: el codigo base confirma el pedido ANTES de cobrar.
    # Si el pago es rechazado, el pedido queda en CONFIRMED sin cobro exitoso.
    # Esta prueba describe el comportamiento ACTUAL, no el deseado.
    gateway = Mock()
    gateway.charge.return_value = False
    order = Order(100)
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(order)
    assert order.status == "CONFIRMED"