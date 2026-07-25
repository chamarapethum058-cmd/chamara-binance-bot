import httpx
import logging
from app.config import settings
from app.database import SessionLocal
from app.models import PreferenceModel

logger = logging.getLogger(__name__)

class TelegramService:
    @staticmethod
    async def get_credentials() -> tuple[str, str]:
        """
        Get token and chat_id from Database preferences with fallback to settings (.env).
        """
        token = ""
        chat_id = ""
        db = SessionLocal()
        try:
            token_pref = db.query(PreferenceModel).filter(PreferenceModel.key == "telegram_bot_token").first()
            chat_pref = db.query(PreferenceModel).filter(PreferenceModel.key == "telegram_chat_id").first()
            token = token_pref.value if token_pref else settings.TELEGRAM_BOT_TOKEN
            chat_id = chat_pref.value if chat_pref else settings.TELEGRAM_CHAT_ID
        except Exception as e:
            logger.error(f"Error fetching telegram credentials from db: {e}")
            token = settings.TELEGRAM_BOT_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID
        finally:
            db.close()
        return (token or "").strip(), (chat_id or "").strip()

    @classmethod
    async def send_message(cls, text: str) -> bool:
        """
        Send a notification message to the configured Telegram chat.
        """
        token, chat_id = await cls.get_credentials()

        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID is missing. Notification not sent.")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    logger.info("Telegram notification sent successfully.")
                    return True
                else:
                    logger.error(f"Failed to send Telegram notification: {response.text}")
                    return False
            except Exception as e:
                logger.error(f"Error sending Telegram notification: {e}")
                return False
