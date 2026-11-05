import re
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_ANALISE = "EM_ANALISE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"


class Customer(BaseModel):
    name: str = Field(..., min_length=3, max_length=120, description="Nome completo do cliente")
    email: str = Field(..., description="E-mail de contato")
    phone: str = Field(..., min_length=8, max_length=20, description="Telefone de contato")
    cpf: str = Field(..., description="CPF do cliente (11 dígitos numéricos ou formatado)")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, value.strip()):
            raise ValueError("Formato de e-mail inválido")
        return value.strip()

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        clean_cpf = re.sub(r"\D", "", value)
        if len(clean_cpf) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos")
        return clean_cpf


class Device(BaseModel):
    device_type: str = Field(..., min_length=2, max_length=50, description="Tipo: Smartphone, Notebook, etc.")
    brand: str = Field(..., min_length=2, max_length=50, description="Marca do aparelho")
    model: str = Field(..., min_length=2, max_length=80, description="Modelo do aparelho")
    serial_number: str = Field(..., min_length=4, max_length=60, description="Número de série único")


class ServiceOrderCreate(BaseModel):
    customer: Customer
    device: Device
    issue_description: str = Field(..., min_length=5, max_length=500, description="Descrição do defeito")
    estimated_price: float = Field(..., gt=0, description="Valor estimado do reparo em reais")


class ServiceOrder(BaseModel):
    id: int
    order_number: str
    customer: Customer
    device: Device
    issue_description: str
    estimated_price: float
    status: OrderStatus
    external_validation_code: Optional[str] = None
    validation_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceOrderResponse(BaseModel):
    id: int
    order_number: str
    customer: Customer
    device: Device
    issue_description: str
    estimated_price: float
    status: OrderStatus
    external_validation_code: Optional[str] = None
    validation_message: Optional[str] = None
    created_at: datetime

