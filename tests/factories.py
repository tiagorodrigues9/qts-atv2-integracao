import random
import re
from typing import Any, Dict, Optional
from faker import Faker
from atv2_integracao.models.order import (
    Customer,
    Device,
    ServiceOrderCreate,
)

faker = Faker("pt_BR")


class CustomerFactory:
    """Factory para geração de dados sintéticos de clientes brasileiros."""

    @classmethod
    def build_dict(cls, **kwargs: Any) -> Dict[str, Any]:
        raw_cpf = faker.cpf()
        clean_cpf = re.sub(r"\D", "", raw_cpf)

        data = {
            "name": faker.name(),
            "email": faker.ascii_safe_email(),
            "phone": faker.cellphone_number()[:14],
            "cpf": clean_cpf,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build(cls, **kwargs: Any) -> Customer:
        return Customer(**cls.build_dict(**kwargs))


class DeviceFactory:
    """Factory para geração de dados sintéticos de equipamentos."""

    DEVICE_TYPES = ["Smartphone", "Notebook", "Tablet", "Smartwatch"]
    BRANDS = ["Apple", "Samsung", "Dell", "Lenovo", "Asus", "Motorola"]

    @classmethod
    def build_dict(cls, **kwargs: Any) -> Dict[str, Any]:
        brand = kwargs.get("brand") or random.choice(cls.BRANDS)
        device_type = kwargs.get("device_type") or random.choice(cls.DEVICE_TYPES)
        model = kwargs.get("model") or f"{brand} {device_type} Plus {random.randint(10, 99)}"
        serial = kwargs.get("serial_number") or f"SN-{faker.bothify(text='??####????').upper()}"

        data = {
            "device_type": device_type,
            "brand": brand,
            "model": model,
            "serial_number": serial,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build(cls, **kwargs: Any) -> Device:
        return Device(**cls.build_dict(**kwargs))


class ServiceOrderFactory:
    """Factory para geração de Ordens de Serviço completas."""

    @classmethod
    def build_dict(
        cls,
        customer_kwargs: Optional[Dict[str, Any]] = None,
        device_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        customer_data = CustomerFactory.build_dict(**(customer_kwargs or {}))
        device_data = DeviceFactory.build_dict(**(device_kwargs or {}))

        data = {
            "customer": customer_data,
            "device": device_data,
            "issue_description": f"Aparelho com falha intermitente na inicialização: {faker.sentence()}",
            "estimated_price": round(random.uniform(150.0, 1800.0), 2),
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_model(cls, **kwargs: Any) -> ServiceOrderCreate:
        data = cls.build_dict(**kwargs)
        return ServiceOrderCreate(**data)

