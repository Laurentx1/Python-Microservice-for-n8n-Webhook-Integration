import logging
import uuid
import time
from app.client import post_with_retry
from app.config import settings
from app.storage import storage
from app.models import CallbackPayload

logger = logging.getLogger(__name__)

async def enrich_data(payload: dict) -> dict:
    """Simulate data enrichment"""
    return {
        **payload,
        "enriched_at": time.time(),
        "processed": True
    }

def transform_data(data: dict) -> dict:
    """Simple data transformation"""
    return {
        "transformed": True,
        "original_data": data
    }

async def process_webhook_task(
    request_data: dict,
    job_id: str,
    callback_url: str | None = None
):
    try:
        # Step 1: Enrich data
        enriched = await enrich_data(request_data["payload"])
        
        # Step 2: Transform data
        transformed = transform_data(enriched)
        
        # Step 3: Send to external API
        headers = {}
        if settings.EXTERNAL_API_KEY:
            headers["Authorization"] = f"Bearer {settings.EXTERNAL_API_KEY}"
        
        await post_with_retry(
            settings.EXTERNAL_API_URL,
            transformed,
            headers=headers
        )
        
        result = {"status": "success", "data": transformed}
        
    except Exception as e:
        result = {"status": "error", "error": str(e)}
        logger.error(f"Processing failed: {str(e)}")
    
    # Save result
    await storage.save_result(job_id, result)
    
    # Step 4: Send callback
    if callback_url:
        callback_payload = CallbackPayload(
            job_id=job_id,
            status=result["status"],
            result=result
        )
        try:
            await post_with_retry(
                callback_url,
                callback_payload.model_dump()
            )
        except Exception as e:
            logger.error(f"Callback failed: {str(e)}")
    
    return result