"""
Supabase client for database operations
"""
from supabase import create_client, Client
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class SupabaseClient:
    """Singleton Supabase client"""
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be configured")

            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Supabase client initialized")

        return cls._instance

    @classmethod
    def get_service_client(cls) -> Client:
        """Get Supabase client with service role key (admin access)"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured")

        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )


def get_supabase() -> Client:
    """Dependency for getting Supabase client"""
    return SupabaseClient.get_client()


def get_supabase_admin() -> Client:
    """Dependency for getting Supabase admin client"""
    return SupabaseClient.get_service_client()
