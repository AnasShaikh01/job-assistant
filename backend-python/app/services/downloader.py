import httpx
from fastapi import HTTPException

class ResumeDownloader:
    """
    Downloads files into memory from a provided URL.
    Stateless and disk-free.
    """
    @staticmethod
    async def download(file_url: str) -> bytes:
        # 30-second timeout to ensure the API doesn't hang on slow Supabase responses
        timeout = httpx.Timeout(30.0)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(file_url)

                # Automatically raises an exception for 4xx and 5xx status codes
                response.raise_for_status()
                return response.content
                
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"Failed to download file. HTTP Status: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Network error or timeout while downloading the file: {str(e)}"
            )