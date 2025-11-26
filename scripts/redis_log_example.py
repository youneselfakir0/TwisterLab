import os

from redis import Redis

# Initialize Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_password = os.getenv("REDIS_PASSWORD", None)

redis_client = Redis(host=redis_host, port=redis_port, password=redis_password)


def log_to_redis(correlation_id, log_message):
    """
    Log a message to Redis with the specified correlation ID.

    :param correlation_id: Unique identifier for the log entry
    :param log_message: The message to log
    """
    redis_key = f"redis:agent:logs:{correlation_id}"
    redis_client.rpush(redis_key, log_message)
    print(f"Logged to Redis under key: {redis_key}")


# Example usage
if __name__ == "__main__":
    test_correlation_id = "12345"
    test_log_message = "This is a test log message."
    log_to_redis(test_correlation_id, test_log_message)
