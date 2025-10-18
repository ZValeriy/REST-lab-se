from fastapi import FastAPI, Depends, status, Query, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from datetime import date
from .models import Client, ClientExtended, ProblemDetails
from . import services
import secrets

app = FastAPI(title="Clients API", version="1.0.0")

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "basic")
    correct_password = secrets.compare_digest(credentials.password, "basic")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/clients", response_model=List[Client], responses={401: {"description": "Unauthorized"}}, tags=["Clients"])
def list_clients(
    created_at_from: Optional[date] = Query(None, description="Дата от"),
    created_at_to: Optional[date] = Query(None, description="Дата до"),
    username: str = Depends(get_current_username),
):
    return services.get_clients(created_at_from, created_at_to)

@app.post(
    "/clients",
    response_model=Client,
    status_code=201,
    responses={
        400: {"model": ProblemDetails},
        409: {"model": ProblemDetails},
        401: {"description": "Unauthorized"},
    },
    tags=["Clients"]
)
def create_client(
    client: Client,
    username: str = Depends(get_current_username),
):
    try:
        return services.create_client(client)
    except HTTPException as e:
        if e.status_code == 409:
            return ProblemDetails(title="Conflict", details=str(e.detail))
        raise

@app.get(
    "/clients/{client_id}",
    response_model=ClientExtended,
    responses={
        200: {"description": "OK"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"}
    },
    tags=["Clients"]
)
def get_client(
    client_id: int,
    username: str = Depends(get_current_username),
):
    return services.get_client_by_id(client_id)