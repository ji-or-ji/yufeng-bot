"""
连接器包 - 负责与外部平台通信
"""

from .base_connector import BaseConnector
from .mock_qq_connector import MockQQConnector

__all__ = ["BaseConnector", "MockQQConnector"]