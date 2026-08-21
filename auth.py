import os
from dotenv import load_dotenv

load_dotenv()  # loads .env at project root

_API_KEY_ENV = "RESEARCH_PIPELINE_API_KEY"


def get_expected_api_key() -> str | None:
    """Read the secret API key from the environment (or .env)."""
    return os.getenv(_API_KEY_ENV)


def verify_api_key(provided: str) -> bool:
    """Return True if the supplied key matches the stored secret."""
    expected = get_expected_api_key()
    return expected is not None and provided == expected
