from typing import List, Optional
from ..models.order import OrderStatus, ServiceOrder, ServiceOrderCreate
from ..repository.memory_repo import OrderRepository, order_repository
from .external_warranty import ExternalWarrantyClient


class OrderService:
    """Regras de negócio para abertura e gestão de Ordens de Serviço."""

    def __init__(
        self,
        repository: OrderRepository = order_repository,
        warranty_client: Optional[ExternalWarrantyClient] = None,
    ):
        self.repository = repository
        self.warranty_client = warranty_client or ExternalWarrantyClient()

    def create_order(self, order_data: ServiceOrderCreate) -> ServiceOrder:
        order_id = self.repository.next_id()
        order_number = self.repository.generate_order_number(order_id)

        # Consulta ao serviço externo de garantia e risco
        external_result = self.warranty_client.check_warranty(
            serial_number=order_data.device.serial_number,
            brand=order_data.device.brand,
            estimated_price=order_data.estimated_price,
        )

        status_str = external_result.get("status", "").upper()
        if status_str == "APPROVED":
            status = OrderStatus.APROVADO
            auth_code = external_result.get("authorization_code", "AUTH-DEFAULT")
            msg = external_result.get("message", "Garantia validada com sucesso.")
        else:
            status = OrderStatus.REJEITADO
            auth_code = None
            msg = external_result.get("message", "Garantia recusada pelo serviço do fabricante.")

        service_order = ServiceOrder(
            id=order_id,
            order_number=order_number,
            customer=order_data.customer,
            device=order_data.device,
            issue_description=order_data.issue_description,
            estimated_price=order_data.estimated_price,
            status=status,
            external_validation_code=auth_code,
            validation_message=msg,
        )

        return self.repository.add(service_order)

    def get_order(self, order_id: int) -> Optional[ServiceOrder]:
        return self.repository.get_by_id(order_id)

    def list_orders(self) -> List[ServiceOrder]:
        return self.repository.list_all()

