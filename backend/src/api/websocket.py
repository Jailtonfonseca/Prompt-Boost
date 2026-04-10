"""
WebSocket Routes - Real-time streaming for recursive reasoning
"""

import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.engines import EngineConfig
from src.providers import ProviderManager
from src.schemas.recursion import StreamMessage
from src.services.recursion_router import RecursionRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["WebSocket"])
provider_manager = ProviderManager()


@router.websocket("/recursion")
async def websocket_recursion(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for streaming recursive reasoning.
    
    Expected message format:
    {
        "type": "stream_start",
        "session_id": "uuid",
        "technique": "self_refine",
        "prompt": "What is...?",
        "max_iterations": 5,
        "temperature": 0.7
    }
    """
    await websocket.accept()
    logger.info("✓ WebSocket client connected")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            msg_type = message.get("type")

            if msg_type == "stream_start":
                await handle_stream_start(websocket, message)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "close":
                break

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "data": f"Unknown message type: {msg_type}",
                    }
                )

    except WebSocketDisconnect:
        logger.info("✓ WebSocket client disconnected")

    except Exception as e:
        logger.error(f"✗ WebSocket error: {e}")
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "data": str(e),
                }
            )
        except Exception:
            pass

    finally:
        try:
            await websocket.close()
        except Exception:
            pass


async def handle_stream_start(websocket: WebSocket, message: dict) -> None:
    """Handle stream_start message."""
    session_id = message.get("session_id", str(uuid.uuid4()))
    technique = message.get("technique", "self_refine")
    prompt = message.get("prompt", "")
    max_iterations = message.get("max_iterations", 5)
    temperature = message.get("temperature", 0.7)
    max_tokens = message.get("max_tokens_per_iteration", 2000)

    logger.info(f"Starting stream: session={session_id}, technique={technique}")

    # Send start message
    await websocket.send_json(
        {
            "type": "status",
            "data": "Session started",
            "metadata": {
                "session_id": session_id,
                "technique": technique,
            },
        }
    )

    try:
        # Create config
        config = EngineConfig(
            max_iterations=max_iterations,
            temperature=temperature,
            max_tokens_per_iteration=max_tokens,
        )

        # Execute engine
        result = await RecursionRouter.execute(technique, prompt, config)

        # Send iterations as they complete
        for i, iteration in enumerate(result.iterations):
            await websocket.send_json(
                {
                    "type": "iteration",
                    "data": {
                        "iteration": i + 1,
                        "response": iteration.response,
                        "quality_score": iteration.quality_score,
                        "tokens_used": iteration.tokens_used,
                    },
                }
            )

        # Send final result
        await websocket.send_json(
            {
                "type": "content",
                "data": result.final_answer,
                "metadata": {
                    "iterations": len(result.iterations),
                    "tokens_used": result.total_tokens_used,
                    "quality_score": result.quality_score,
                    "execution_time_ms": result.execution_time_ms,
                },
            }
        )

        # Send completion
        await websocket.send_json(
            {
                "type": "end",
                "data": "Stream completed",
                "metadata": {
                    "session_id": session_id,
                    "status": result.status.value,
                },
            }
        )

    except Exception as e:
        logger.error(f"Stream error: {e}")
        await websocket.send_json(
            {
                "type": "error",
                "data": str(e),
            }
        )


@router.websocket("/debug")
async def websocket_debug(websocket: WebSocket) -> None:
    """
    Debug WebSocket endpoint for testing.
    
    Echo server that returns all received messages.
    """
    await websocket.accept()
    logger.info("✓ Debug WebSocket client connected")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")

            # Echo back
            await websocket.send_json(
                {
                    "type": "echo",
                    "data": data,
                    "timestamp": str(datetime.now()),
                }
            )

    except WebSocketDisconnect:
        logger.info("✓ Debug WebSocket client disconnected")

    except Exception as e:
        logger.error(f"✗ Debug WebSocket error: {e}")

    finally:
        try:
            await websocket.close()
        except Exception:
            pass
