import os
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Supabase configuration for Driveline Recruit
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://lqllzavksufpiqefwthy.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxxbGx6YXZrc3VmcGlxZWZ3dGh5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzc3Njc1MiwiZXhwIjoyMDY5MzUyNzUyfQ.cMbhS0BNWy6eXSLsMk9LVw8Y7pkwJsFLBNyY9yPNS8Y')

# Create Supabase client
try:
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully for Driveline Recruit")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    supabase_client = None

def get_supabase_client():
    """Get the Supabase client instance"""
    return supabase_client

def test_connection():
    """Test the Supabase connection"""
    try:
        if not supabase_client:
            return False, "Supabase client not initialized"
        
        # Try to query the driver_profiles table
        result = supabase_client.table('driver_profiles').select('id').limit(1).execute()
        return True, "Connection successful"
        
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

