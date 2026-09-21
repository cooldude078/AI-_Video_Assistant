import os
import time

import httpx


def invoke_with_rate_limit(chain, value):
    """Invoke a model chain with bounded backoff for HTTP 429 responses."""
    max_retries = int(os.getenv("GROQ_MAX_RETRIES", os.getenv("MISTRAL_MAX_RETRIES", "3")))

    for attempt in range(max_retries + 1):
        try:
            return chain.invoke(value)
        except httpx.HTTPStatusError as error:
            response = error.response
            if response is None or response.status_code != 429:
                raise

            if attempt == max_retries:
                raise RuntimeError(
                    "Groq API rate limit is still active. Wait for the limit to "
                    "reset or check your GROQ_API_KEY quota."
                ) from error

            retry_after = response.headers.get("retry-after")
            try:
                delay = float(retry_after) if retry_after else 10 * (2**attempt)
            except ValueError:
                delay = 10 * (2**attempt)

            time.sleep(min(delay, 60))