import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings
from app.exceptions import ExternalAPIError

@retry(
    stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_FACTOR),
    reraise=True
)
async def post_with_retry(url: str, data: dict, headers: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise ExternalAPIError(f"External API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise ExternalAPIError(f"Request failed: {str(e)}") from e