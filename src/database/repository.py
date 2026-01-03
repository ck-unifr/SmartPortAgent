# src/database/repository.py
import json
from contextlib import contextmanager
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.database.models import ChatLog, SessionLocal, init_db

# 确保启动时初始化表
init_db()


@contextmanager
def get_db():
    """数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatLogRepository:
    @staticmethod
    def save_log(
        user_input: str,
        ai_output: str,
        latency: float,
        token_usage: Dict[str, int],
        intermediate_steps: List[Dict],
        rag_sources: List[str],
        status: str = "success",
        error_msg: str = None,
    ):
        """保存单次对话日志"""
        with get_db() as db:
            log_entry = ChatLog(
                user_input=user_input,
                ai_output=ai_output,
                latency=latency,
                input_tokens=token_usage.get("input", 0),
                output_tokens=token_usage.get("output", 0),
                total_tokens=token_usage.get("total", 0),
                intermediate_steps=intermediate_steps,  # SQLAlchemy处理JSON序列化
                rag_sources=rag_sources,
                status=status,
                error_message=error_msg,
            )
            db.add(log_entry)
            db.commit()
            return log_entry.id

    @staticmethod
    def get_recent_logs(limit: int = 50):
        """获取最近的日志记录"""
        with get_db() as db:
            return (
                db.query(ChatLog).order_by(ChatLog.timestamp.desc()).limit(limit).all()
            )

    @staticmethod
    def clear_logs():
        """清空所有审计日志"""
        with get_db() as db:
            try:
                # 批量删除所有记录
                num_deleted = db.query(ChatLog).delete()
                db.commit()
                return num_deleted
            except Exception as e:
                db.rollback()
                print(f"❌ 清空数据库失败: {e}")
                return 0
