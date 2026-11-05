import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models.order import (
    Customer,
    Device,
    ServiceOrderCreate,
    ServiceOrderResponse,
)
from .repository.memory_repo import order_repository
from .services.external_warranty import ExternalServiceException, ExternalWarrantyClient
from .services.order_service import OrderService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="TechCare OS API",
    description="Sistema de Gestão de Ordens de Serviço & Validação de Garantia",
    version="1.0.0",
)

# Montagem de arquivos estáticos e templates Jinja2
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Serviço principal de ordens de serviço
order_service = OrderService(repository=order_repository)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de checagem de integridade da aplicação."""
    return {"status": "healthy", "service": "TechCare OS"}


# ==============================================================================
# Rotas Web (Interface HTML - WCAG 2.1 AA)
# ==============================================================================

@app.get("/", response_class=HTMLResponse, tags=["Web"])
def home_page(
    request: Request,
    alert_message: Optional[str] = None,
    alert_type: Optional[str] = None,
):
    orders = order_service.list_orders()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "orders": orders,
            "alert_message": alert_message,
            "alert_type": alert_type or "success",
        },
    )


@app.post("/orders", response_class=HTMLResponse, tags=["Web"])
def submit_order_form(
    request: Request,
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    customer_phone: str = Form(...),
    customer_cpf: str = Form(...),
    device_type: str = Form(...),
    device_brand: str = Form(...),
    device_model: str = Form(...),
    device_serial: str = Form(...),
    issue_description: str = Form(...),
    estimated_price: float = Form(...),
):
    try:
        order_create = ServiceOrderCreate(
            customer=Customer(
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                cpf=customer_cpf,
            ),
            device=Device(
                device_type=device_type,
                brand=device_brand,
                model=device_model,
                serial_number=device_serial,
            ),
            issue_description=issue_description,
            estimated_price=estimated_price,
        )
        created_order = order_service.create_order(order_create)
        msg = f"Ordem {created_order.order_number} cadastrada com sucesso! Status: {created_order.status.value}."
        return home_page(request, alert_message=msg, alert_type="success")
    except ExternalServiceException as exc:
        msg = f"Falha na comunicação com o serviço externo: {str(exc)}"
        return home_page(request, alert_message=msg, alert_type="error")
    except ValueError as exc:
        msg = f"Dados inválidos: {str(exc)}"
        return home_page(request, alert_message=msg, alert_type="error")


# ==============================================================================
# Rotas REST API (JSON)
# ==============================================================================

@app.get("/api/orders", response_model=List[ServiceOrderResponse], tags=["Orders"])
def list_orders():
    """Lista todas as ordens de serviço cadastradas."""
    return order_service.list_orders()


@app.post(
    "/api/orders",
    response_model=ServiceOrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"],
)
def create_order(payload: ServiceOrderCreate):
    """
    Cria uma nova ordem de serviço com validação de garantia externa.
    Retorna HTTP 201 com os dados da OS ou HTTP 502 se a API externa falhar.
    """
    try:
        return order_service.create_order(payload)
    except ExternalServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha na comunicação com o serviço externo de garantia: {str(exc)}",
        )


@app.get(
    "/api/orders/{order_id}",
    response_model=ServiceOrderResponse,
    tags=["Orders"],
)
def get_order(order_id: int):
    """Obtém detalhes de uma ordem de serviço pelo ID."""
    order = order_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada",
        )
    return order


def start():
    """Inicia o servidor Uvicorn em modo standalone."""
    import uvicorn
    uvicorn.run("atv2_integracao.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    start()

