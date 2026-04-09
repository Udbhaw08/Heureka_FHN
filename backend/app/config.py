from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Postgres async URL
    DATABASE_URL: str

    # Agent service URLs (your teammates will run these)
    SKILL_AGENT_URL: str = "http://localhost:8003"
    BIAS_AGENT_URL: str = "http://localhost:8002"
    MATCH_AGENT_URL: str = "http://localhost:8001"
    ATS_AGENT_URL: str = "http://localhost:8004"
    GITHUB_AGENT_URL: str = "http://localhost:8005"
    LEETCODE_AGENT_URL: str = "http://localhost:8006"
    CODEFORCES_AGENT_URL: str = "http://localhost:8011"
    LINKEDIN_AGENT_URL: str = "http://localhost:8007"
    TEST_AGENT_URL: str = "http://localhost:8009"
    PASSPORT_AGENT_URL: str = "http://localhost:8008"

    # Ed25519 signing keys (base64 raw)
    # Provided with defaults for demo purposes; override in production
    SIGNING_PRIVATE_KEY_B64: str = "J2nzAJ7R0oA9zjTOhApGtngr02uoFh4SamqSOGqL2Fk="
    SIGNING_PUBLIC_KEY_B64: str = "pMOiQrt/a30izmUSA1jOAM4DStxe6iIZPlcVXLAxYSA="

    # Simple app secret (optional)
    APP_SECRET: str = "dev-secret"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
