from typing import List, Optional
from datetime import date
from fastapi import HTTPException
from .models import Client, ClientExtended

# In-memory хранилище
clients_db: dict[int, ClientExtended] = {}

def get_clients(created_at_from: Optional[date], created_at_to: Optional[date]) -> List[Client]:
    result = []

    for client in clients_db.values():
        if created_at_from and client.created_at < created_at_from:
            continue
        if created_at_to and client.created_at > created_at_to:
            continue
        result.append(Client(**client.dict()))

    return result

def create_client(client: Client) -> Client:
    if client.id in clients_db:
        raise HTTPException(status_code=409, detail="Client with this ID already exists")

    for existing in clients_db.values():
        if existing.login == client.login:
            raise HTTPException(status_code=409, detail="Client with this login already exists")

    extended = ClientExtended(**client.dict())
    clients_db[client.id] = extended
    return client

def get_client_by_id(client_id: int) -> ClientExtended:
    client = clients_db.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client