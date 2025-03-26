# core/utils.py
import requests
from fastapi import HTTPException

def make_api_request(
    url: str,
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    timeout: int = 30
) -> dict:
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"API грешка: {str(e)}"
        )
