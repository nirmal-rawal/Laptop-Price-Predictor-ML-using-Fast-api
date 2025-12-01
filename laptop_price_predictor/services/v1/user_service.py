import logging
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


def track_user_activity(
    user_ip: Optional[str], 
    endpoint: str,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """Track user activity for analytics (functional approach - no OOP needed)"""
    try:
        activity_data = {
            "user_ip": user_ip,
            "endpoint": endpoint,
            "user_agent": user_agent,
            "timestamp": None  # Will be set by repository
        }
        
        logger.info(f"User activity tracked: {endpoint} from {user_ip}")
        return activity_data
        
    except Exception as e:
        logger.error(f"Failed to track user activity: {e}")
        return {}