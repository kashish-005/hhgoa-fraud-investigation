import requests
import os
from dotenv import load_dotenv

load_dotenv()

TG_BASE_URL = os.getenv("TG_URL") or os.getenv("TG_HOST")
HEADERS = {"Authorization": f"Bearer {os.getenv('TG_TOKEN')}"}

def get_transaction_history(customer_id: str):
    """Fetches the latest 50 transactions for a given customer."""
    url = f"{TG_BASE_URL}/get_transaction_history"
    response = requests.get(url, headers=HEADERS, params={"customer_id": customer_id})
    return response.json()

def get_connected_entities(transaction_id: str):
    """Traverses the graph to find devices, emails, and regions linked to a transaction."""
    url = f"{TG_BASE_URL}/get_connected_entities"
    response = requests.get(url, headers=HEADERS, params={"transaction_id": transaction_id})
    return response.json()

def get_prior_cases(card_id: str):
    """Checks if a credit card was involved in previous closed fraud investigations."""
    url = f"{TG_BASE_URL}/get_prior_cases"
    response = requests.get(url, headers=HEADERS, params={"card_id": card_id})
    return response.json()