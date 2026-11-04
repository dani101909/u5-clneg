from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_repository_commit():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.commit()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120
    engine.dispose()


def test_repository_rollback():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.rollback()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None
    engine.dispose()


def test_repository_commit_order_250():
    engine = make_engine()
    with Session(engine) as session:
        # Arrange: pedido nuevo de 250 que se guardará con id=2
        SqlOrderRepository(session).save(2, Order(250))
        # Act: confirmar la transacción para que el registro sea persistente
        session.commit()
        # Assert: consultar por id y verificar id, total y estado
        row = session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert row is not None
        assert row.id == 2
        assert row.total == 250
        assert row.status == "NEW"
    engine.dispose()