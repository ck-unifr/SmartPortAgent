# src/database/models.py
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    JSON,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

# 假设在 settings 中增加了 DB_PATH，如果没有，默认用 local.db
DB_URL = f"sqlite:///{settings.DB_PATH}"

Base = declarative_base()


class ChatLog(Base):
    """
    对话日志表
    记录用户输入、AI输出、中间过程、Token消耗及性能指标
    """

    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), index=True, nullable=True, comment="会话ID")
    timestamp = Column(DateTime, default=datetime.now, index=True, comment="记录时间")

    # 核心对话内容
    user_input = Column(Text, nullable=False, comment="用户提问")
    ai_output = Column(Text, nullable=True, comment="AI回答")

    # 诊断与审计信息
    intermediate_steps = Column(JSON, nullable=True, comment="工具调用链详情")
    rag_sources = Column(JSON, nullable=True, comment="RAG引用文档")

    # 性能指标
    latency = Column(Float, comment="总耗时(秒)")
    total_tokens = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    # 元数据
    model_name = Column(String(50), nullable=True)
    status = Column(String(20), default="success", comment="success/error")
    error_message = Column(Text, nullable=True)


# 初始化数据库连接
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库表结构"""
    Base.metadata.create_all(bind=engine)
