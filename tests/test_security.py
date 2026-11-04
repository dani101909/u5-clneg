from datetime import UTC, datetime, timedelta

from src.security import can_cancel

# Fecha fija para que las pruebas nuevas den siempre el mismo resultado
NOW = datetime(2026, 11, 4, 12, 0, 0, tzinfo=UTC)

def test_owner_within_24h():
    now = datetime.now(UTC)
    assert can_cancel("NEW", 1, 1, False, now - timedelta(hours=1), now)

def test_stranger_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 2, False, now, now)

def test_shipped_denied_even_admin():
    now = datetime.now(UTC)
    assert not can_cancel("SHIPPED", 1, 1, True, now, now)

def test_expired_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 1, False, now - timedelta(hours=25), now)

def test_admin_cancels_new_order_of_another_user():
    # Admin (usuario 99) cancela un pedido NEW cuyo propietario es el usuario 1
    created_at = NOW - timedelta(hours=1)
    assert can_cancel("NEW", 1, 99, True, created_at, NOW)

def test_admin_cancels_old_new_order():
    # El administrador no tiene limite de 24 horas
    created_at = NOW - timedelta(hours=48)
    assert can_cancel("NEW", 1, 99, True, created_at, NOW)

def test_owner_exactly_24h_denied():
    # Limite: a las 24 horas exactas ya no se permite (la regla es "menos de 24 h")
    created_at = NOW - timedelta(hours=24)
    assert not can_cancel("NEW", 1, 1, False, created_at, NOW)

def test_owner_just_under_24h_allowed():
    # Limite: un minuto antes de cumplir 24 horas todavia se permite
    created_at = NOW - timedelta(hours=23, minutes=59)
    assert can_cancel("NEW", 1, 1, False, created_at, NOW)