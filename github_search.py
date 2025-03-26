import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from dateutil import parser
from core.utils import make_api_request

router = APIRouter(tags=["GitHub Search"])
logger = logging.getLogger(__name__)

# ==============================================
GITHUB_API_KEY = "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"  # 
# ==============================================

class GitHubQuery(BaseModel):
    query: str = Field(..., min_length=3, example="python trading bot", max_length=100)
    per_page: int = Field(default=10, ge=1, le=30)

class GitHubRepoItem(BaseModel):
    name: str
    url: str
    description: Optional[str]
    stars: int = Field(..., ge=0)
    language: Optional[str]
    license: Optional[str]
    last_updated: datetime

def validate_response_item(item: dict) -> bool:
    required_fields = ["full_name", "html_url", "stargazers_count", "updated_at"]
    return all(field in item for field in required_fields)

@router.post("/github", response_model=List[GitHubRepoItem], summary="Търсене в GitHub репозитории")
async def search_github_repos(data: GitHubQuery):
    """
    Заявка към GitHub API с интегрирана валидация и обработка на грешки
    """
    try:
        # Проверка за тестов токен
        if "ВАШИЯТ_ТОКЕН" in GITHUB_API_KEY:
            logger.error("Невалидна конфигурация на токена")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидна конфигурация на API ключ"
            )

        # Конфигуриране на заявката
        params = {
            "q": data.query,
            "per_page": data.per_page,
            "sort": "updated",
            "order": "desc"
        }

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_API_KEY}"
        }

        # Изпращане на заявка
        response = await make_api_request(
            url="https://api.github.com/search/repositories",
            method="GET",
            headers=headers,
            params=params
        )

        # Нормализация на данните
        normalized_results = []
        for item in response.get("items", []):
            if not validate_response_item(item):
                logger.warning("Пропуснат невалиден запис")
                continue
                
            try:
                normalized_results.append(GitHubRepoItem(
                    name=item["full_name"],
                    url=item["html_url"],
                    description=item.get("description"),
                    stars=item["stargazers_count"],
                    language=item.get("language"),
                    license=item.get("license", {}).get("name"),
                    last_updated=parser.parse(item["updated_at"])
                ))
            except Exception as e:
                logger.error(f"Грешка при нормализация: {str(e)}")
                continue

        return normalized_results

    except HTTPException as he:
        logger.error(f"API грешка: {he.detail}")
        raise
    except Exception as e:
        logger.critical(f"Критична грешка: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Вътрешна грешка в сървъра"
        )
