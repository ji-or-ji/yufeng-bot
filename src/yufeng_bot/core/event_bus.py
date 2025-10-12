# src/yufeng_bot/core/event_bus.py
"""
事件总线 - 项目的神经中枢
负责所有组件间的异步通信
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """事件处理优先级"""
    HIGHEST = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    LOWEST = 0

@dataclass
class Event:
    """事件数据类"""
    name: str
    data: Any
    source: str
    timestamp: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class EventBus:
    """
    事件总线核心类
    实现发布-订阅模式，支持异步事件处理
    """
    
    def __init__(self):
        # 存储事件处理器: {event_name: [(priority, handler, filter_func)]}
        self._handlers: Dict[str, List] = {}
        # 事件统计
        self._stats = {"events_processed": 0, "handlers_called": 0}
        # 运行状态
        self._running = False
        # 任务跟踪
        self._active_tasks = set()
    
    async def start(self):
        """启动事件总线"""
        self._running = True
        logger.info("事件总线已启动")
    
    async def stop(self):
        """停止事件总线"""
        self._running = False
        # 等待所有任务完成
        if self._active_tasks:
            await asyncio.wait(self._active_tasks, timeout=10.0)
        logger.info("事件总线已停止")
    
    def subscribe(self, 
                 event_name: str, 
                 handler: Callable, 
                 priority: EventPriority = EventPriority.NORMAL,
                 filter_func: Optional[Callable] = None):
        """
        订阅事件
        
        Args:
            event_name: 事件名称
            handler: 事件处理函数
            priority: 处理优先级
            filter_func: 事件过滤函数
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        
        # 按优先级从高到低排序
        handlers = self._handlers[event_name]
        new_handler = (priority.value, handler, filter_func)
        
        # 找到正确的插入位置（保持从高到低排序）
        insert_index = len(handlers)
        for i, (existing_priority, _, _) in enumerate(handlers):
            if priority.value > existing_priority:
                insert_index = i
                break
        
        handlers.insert(insert_index, new_handler)
        logger.debug(f"已订阅事件: {event_name}, 优先级: {priority}")
    
    def unsubscribe(self, event_name: str, handler: Callable):
        """取消订阅事件"""
        if event_name in self._handlers:
            self._handlers[event_name] = [
                (p, h, f) for p, h, f in self._handlers[event_name] 
                if h != handler
            ]
            logger.debug(f"已取消订阅事件: {event_name}")
    
    async def publish(self, event_name: str, data: Any, source: str = "system", **metadata) -> List[Any]:
        """
        发布事件
        
        Args:
            event_name: 事件名称
            data: 事件数据
            source: 事件来源
            metadata: 附加元数据
            
        Returns:
            所有处理器的返回结果列表
        """
        if not self._running:
            logger.warning("事件总线未启动，忽略事件发布")
            return []
        
        event = Event(
            name=event_name,
            data=data,
            source=source,
            timestamp=asyncio.get_event_loop().time(),
            metadata=metadata
        )
        
        self._stats["events_processed"] += 1
        logger.debug(f"发布事件: {event_name} from {source}")
        
        # 收集所有处理结果
        results = []
        
        if event_name in self._handlers:
            for priority, handler, filter_func in self._handlers[event_name]:
                # 应用过滤器
                if filter_func and not filter_func(event):
                    continue
                
                try:
                    # 执行处理器
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(event)
                    else:
                        result = handler(event)
                    
                    results.append(result)
                    self._stats["handlers_called"] += 1
                    
                except Exception as e:
                    logger.error(f"事件处理器错误 [{event_name}]: {e}", exc_info=True)
        
        return results
    
    async def request(self, event_name: str, data: Any, source: str = "system", timeout: float = 10.0, **metadata) -> Any:
        """
        发布请求事件并等待第一个响应
        """
        # 设置请求标识
        metadata["is_request"] = True
        metadata["request_id"] = f"req_{asyncio.get_event_loop().time()}"
        
        # 发布请求事件并等待所有处理器完成
        responses = await self.publish(event_name, data, source, **metadata)
        
        # 返回第一个非None的响应
        for response in responses:
            if response is not None:
                return response
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取事件总线统计信息"""
        return self._stats.copy()

# 全局事件总线实例
event_bus = EventBus()

# 常用事件名称常量类
class EventNames:
    """预定义事件名称"""
    # 消息相关
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_PROCESSED = "message.processed"
    MESSAGE_SENDING = "message.sending"
    MESSAGE_SENT = "message.sent"
    
    # 插件相关
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"
    
    # 系统相关
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    CONFIG_CHANGED = "config.changed"
    
    # 人格相关
    PERSONALITY_CHANGED = "personality.changed"
    EMOTION_UPDATED = "emotion.updated"
    
    # 请求类型
    WEATHER_REQUEST = "request.weather"
    SEARCH_REQUEST = "request.search"
    CALCULATION_REQUEST = "request.calculation"