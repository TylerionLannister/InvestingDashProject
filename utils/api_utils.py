import time

def safe_api_call(func, *args, retries=5, wait_on_429=30, **kwargs):
    attempts = 0

    while attempts < retries:
        try:
            return func(*args, **kwargs)

        except Exception as e:

            if "429" in str(e):
                attempts += 1
                print(
                    f"Rate limit hit on {func.__name__}. "
                    f"Waiting {wait_on_429}s... "
                    f"(attempt {attempts}/{retries})"
                )
                time.sleep(wait_on_429)

            else:
                print(f"Error in {func.__name__}: {e}")
                return None

    print(f"Max retries reached for {func.__name__}")
    return None