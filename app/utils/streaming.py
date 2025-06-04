import json
import logging
from typing import Callable, Generator, Optional, Union
from fastapi.responses import StreamingResponse
from app.sessionDB.database import async_session_maker
from app.sessionDB.models import Message
from app.sessionDB.session_logic import get_or_create_active_session

logger = logging.getLogger(__name__)

def stream_response(
    generator_func: Callable[..., Optional[Generator[Union[str, bytes], None, None]]],
    question: Optional[str] = "",
    user_id: str = "anon",
    model: str = "ollama"
):
    async def stream():
        collected_response = ""

        try:
            generator = generator_func(question) if question else generator_func()
            if generator is None:
                logger.error("⚠️ Generator function returned None")
                yield f"data: ❌ Модель не відповіла або виникла помилка.\n\n"
                return
        except TypeError as e:
            logger.error(f"🛑 Generator function call failed: {e}")
            yield f"data: ❌ Помилка виклику моделі: {str(e)}\n\n"
            return
        except Exception as e:
            logger.error(f"❌ Unexpected error during generator init: {e}")
            yield f"data: ❌ Внутрішня помилка при ініціалізації моделі\n\n"
            return

        for chunk in generator:
            try:
                if isinstance(chunk, bytes):
                    chunk = chunk.decode("utf-8")

                if not chunk.strip().startswith("{"):
                    collected_response += chunk
                    yield f"data: {chunk}\n\n"
                    continue

                data = json.loads(chunk)
                response_piece = data.get("response")

                if response_piece:
                    collected_response += response_piece
                    yield f"data: {response_piece}\n\n"

            except Exception as e:
                logger.error(f"⚠️ Chunk parse error: {e}")
                continue

        if question and collected_response:
            await log_chat_to_db(question, collected_response, user_id, model)

    return stream


async def log_chat_to_db(user_input: str, bot_response: str, user_id: str, model: str):
    logger.info("📥 log_chat_to_db called")
    logger.info(f"User ID for session: {user_id}")
    logger.info(f"user_input: {user_input}")
    logger.info(f"bot_response: {bot_response}")
    logger.info(f"bot_LLM: {model}")

    session_id = await get_or_create_active_session(user_id, model)

    async with async_session_maker() as db:
        db.add_all([
            Message(session_id=session_id, role="user", content=user_input),
            Message(session_id=session_id, role="assistant", content=bot_response)
        ])
        await db.commit()
        logger.info(f"✅ Chat logged to session {session_id}")
