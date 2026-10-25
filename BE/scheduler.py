from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from subscription.repository import get_expired_subscriptions
from users.repository import update_user_tier
from users.model import Tier
import logging
from subscription.repository import update_subscription_end_date
from users.repository import get_user_by_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_expired_subscriptions_job():
    """Daily job to check and reset users whose subscription period has ended"""
    try:
        logger.info("Starting daily expired subscriptions check...")
        expired_subscriptions = get_expired_subscriptions()
        reset_users = []
        
        for subscription in expired_subscriptions:
            try:
                # Get user directly by user_id 
                user = get_user_by_id(subscription.user_id)
                if user:
                    update_user_tier(user.email, Tier.FREE, is_subscribed=False)
                    update_subscription_end_date(user.email, None)
                    reset_users.append(user.email)
                    logger.info(f"Reset expired subscription for user: {user.email}")
                else:
                    logger.warning(f"User not found for subscription user_id: {subscription.user_id}")

                
            except Exception as user_error:
                logger.error(f"Error processing subscription {subscription.id}: {str(user_error)}")
        
        logger.info(f"Daily check completed. Processed {len(reset_users)} expired subscriptions: {reset_users}")
        
    except Exception as e:
        logger.error(f"Error in daily expired subscriptions check: {str(e)}")

def start_scheduler():
    """Start the scheduler"""
    try:
        # Add the job to run daily at 2:00 AM
        scheduler.add_job(
            check_expired_subscriptions_job,
            CronTrigger(hour=2, minute=0),  # Run at 2:00 AM daily
            id='check_expired_subscriptions',
            name='Check and reset expired subscriptions',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")

def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}") 