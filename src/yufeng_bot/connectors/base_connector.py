"""
连接器基础类
定义所有连接器必须实现的接口
"""
import abc
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseConnector(abc.ABC):
    """连接器抽象基类"""
    
    def __init__(self):
        self.name = "base_connector"
        self.version = "1.0.0"
    
    @abc.abstractmethod
    async def initialize(self):
        """初始化连接器"""
        pass
    
    @abc.abstractmethod
    async def close(self):
        """关闭连接器"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "unknown"
        }