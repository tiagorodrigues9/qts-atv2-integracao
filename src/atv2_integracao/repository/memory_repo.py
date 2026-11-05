from typing import Dict, List, Optional
from threading import Lock
from ..models.order import ServiceOrder


class OrderRepository:
    """Repositório em memória para persistência de ordens de serviço."""

    def __init__(self) -> None:
        self._orders: Dict[int, ServiceOrder] = {}
        self._current_id = 0
        self._lock = Lock()

    def next_id(self) -> int:
        with self._lock:
            self._current_id += 1
            return self._current_id

    def generate_order_number(self, order_id: int) -> str:
        return f"OS-2026-{order_id:04d}"

    def add(self, order: ServiceOrder) -> ServiceOrder:
        with self._lock:
            self._orders[order.id] = order
            return order

    def get_by_id(self, order_id: int) -> Optional[ServiceOrder]:
        with self._lock:
            return self._orders.get(order_id)

    def list_all(self) -> List[ServiceOrder]:
        with self._lock:
            # Retorna lista ordenada decrescente por ID
            return sorted(self._orders.values(), key=lambda o: o.id, reverse=True)

    def clear(self) -> None:
        """Limpa todos os registros (usado em teardown de fixtures)."""
        with self._lock:
            self._orders.clear()
            self._current_id = 0


# Instância global padrão do repositório
order_repository = OrderRepository()

