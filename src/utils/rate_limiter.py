"""
Rate limiter implementation for API calls with burst control and error handling.
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any, Callable
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    calls_per_second: float
    burst_limit: Optional[int] = None
    daily_limit: Optional[int] = None
    hourly_limit: Optional[int] = None
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay_ms: int = 1000
    max_delay_ms: int = 32000
    max_attempts: int = 3
    timeout_ms: int = 30000


class RateLimiter:
    """Thread-safe rate limiter with burst control."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.min_interval = 1.0 / config.calls_per_second
        self.burst_limit = config.burst_limit or int(config.calls_per_second * 2)
        self.call_times = deque(maxlen=self.burst_limit)
        self.lock = asyncio.Lock()
        self.daily_calls = 0
        self.hourly_calls = 0
        self.daily_reset_time = time.time() + 86400
        self.hourly_reset_time = time.time() + 3600

    async def acquire(self):
        """Acquire permission to make an API call."""
        async with self.lock:
            now = time.time()

            # Reset counters if needed
            if now > self.daily_reset_time:
                self.daily_calls = 0
                self.daily_reset_time = now + 86400

            if now > self.hourly_reset_time:
                self.hourly_calls = 0
                self.hourly_reset_time = now + 3600

            # Check daily/hourly limits
            if self.config.daily_limit and self.daily_calls >= self.config.daily_limit:
                sleep_time = self.daily_reset_time - now
                logger.warning(f"Daily limit reached. Sleeping for {sleep_time:.0f} seconds")
                await asyncio.sleep(sleep_time)
                now = time.time()
                self.daily_calls = 0

            if self.config.hourly_limit and self.hourly_calls >= self.config.hourly_limit:
                sleep_time = self.hourly_reset_time - now
                logger.warning(f"Hourly limit reached. Sleeping for {sleep_time:.0f} seconds")
                await asyncio.sleep(sleep_time)
                now = time.time()
                self.hourly_calls = 0

            # Remove old timestamps outside window
            while self.call_times and self.call_times[0] < now - 1.0:
                self.call_times.popleft()

            # Check burst limit
            if len(self.call_times) >= self.burst_limit:
                sleep_time = 1.0 - (now - self.call_times[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    now = time.time()

            # Check rate limit
            if self.call_times:
                elapsed = now - self.call_times[-1]
                if elapsed < self.min_interval:
                    await asyncio.sleep(self.min_interval - elapsed)
                    now = time.time()

            self.call_times.append(now)
            self.daily_calls += 1
            self.hourly_calls += 1


class RetryHandler:
    """Handle retries with various backoff strategies."""

    def __init__(self, config: RateLimitConfig):
        self.config = config

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        delay_ms = self.config.base_delay_ms

        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # Check if error is retryable
                if not self._is_retryable(e):
                    raise

                if attempt < self.config.max_attempts - 1:
                    # Calculate delay based on strategy
                    if self.config.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        delay_ms = min(delay_ms * 2, self.config.max_delay_ms)
                    elif self.config.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
                        delay_ms = min(
                            self.config.base_delay_ms * (attempt + 1),
                            self.config.max_delay_ms
                        )
                    # FIXED_DELAY uses base_delay_ms without modification

                    logger.info(f"Retry {attempt + 1}/{self.config.max_attempts} "
                              f"after {delay_ms}ms: {str(e)}")
                    await asyncio.sleep(delay_ms / 1000)

        raise last_exception

    def _is_retryable(self, exception: Exception) -> bool:
        """Determine if an exception is retryable."""
        # Check for specific HTTP status codes
        if hasattr(exception, 'status_code'):
            retryable_codes = {429, 500, 502, 503, 504}
            return exception.status_code in retryable_codes

        # Check for network-related errors
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return True

        return False


class APIClientBase:
    """Base class for API clients with rate limiting."""

    def __init__(self, config: RateLimitConfig):
        self.rate_limiter = RateLimiter(config)
        self.retry_handler = RetryHandler(config)
        self.config = config

    async def make_request(self, endpoint: str, **kwargs) -> Any:
        """Make rate-limited API request."""
        await self.rate_limiter.acquire()

        async def _request():
            # This would be replaced with actual HTTP request
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_ms / 1000)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(endpoint, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()

        return await self.retry_handler.execute_with_retry(_request)


# Decorator for rate limiting
def rate_limited(limiter: RateLimiter):
    """Decorator to rate limit function calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await limiter.acquire()
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Factory for creating rate limiters from config
class RateLimiterFactory:
    """Factory for creating rate limiters from API specifications."""

    _limiters: Dict[str, RateLimiter] = {}

    @classmethod
    def get_limiter(cls, api_name: str, config: Dict[str, Any]) -> RateLimiter:
        """Get or create a rate limiter for an API."""
        if api_name not in cls._limiters:
            rate_config = RateLimitConfig(
                calls_per_second=config.get('calls_per_second', 1),
                burst_limit=config.get('burst_limit'),
                daily_limit=config.get('daily_limit'),
                hourly_limit=config.get('hourly_limit'),
                retry_strategy=RetryStrategy(config.get('retry_strategy', 'exponential_backoff')),
                base_delay_ms=config.get('base_delay_ms', 1000),
                max_delay_ms=config.get('max_delay_ms', 32000),
                max_attempts=config.get('max_attempts', 3),
                timeout_ms=config.get('timeout_ms', 30000)
            )
            cls._limiters[api_name] = RateLimiter(rate_config)

        return cls._limiters[api_name]


# Example usage
if __name__ == "__main__":
    import aiohttp

    async def example():
        # Create rate limiter for OpenAlex API
        config = RateLimitConfig(
            calls_per_second=10,
            burst_limit=20,
            daily_limit=100000,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )

        limiter = RateLimiter(config)

        # Use as decorator
        @rate_limited(limiter)
        async def fetch_data(url):
            print(f"Fetching {url}")
            # Actual API call would go here
            return {"data": "example"}

        # Make multiple requests
        urls = [f"https://api.example.com/item/{i}" for i in range(20)]
        tasks = [fetch_data(url) for url in urls]
        results = await asyncio.gather(*tasks)
        print(f"Fetched {len(results)} items")

    # Run example
    # asyncio.run(example())
