# tests/test_event_bus.py
import asyncio
import pytest
from src.yufeng_bot.core.event_bus import EventBus, EventPriority, EventNames

@pytest.fixture
def event_bus_instance():
    """创建事件总线实例"""
    bus = EventBus()
    return bus

@pytest.mark.asyncio
async def test_event_subscription_and_publication(event_bus_instance):
    """测试事件订阅和发布"""
    bus = event_bus_instance
    await bus.start()
    
    # 收集处理结果的列表
    results = []
    
    # 定义事件处理器
    async def test_handler(event):
        results.append(f"处理了事件: {event.name}")
        return f"处理结果: {event.data}"
    
    # 订阅事件
    bus.subscribe("test.event", test_handler)
    
    # 发布事件
    await bus.publish("test.event", "测试数据", source="test")
    
    # 验证结果
    assert len(results) == 1
    assert "处理了事件: test.event" in results[0]
    
    await bus.stop()

@pytest.mark.asyncio
async def test_event_priority(event_bus_instance):
    """测试事件优先级"""
    bus = event_bus_instance
    await bus.start()
    
    execution_order = []
    
    # 定义不同优先级的事件处理器
    async def low_priority_handler(event):
        execution_order.append("low")
    
    async def high_priority_handler(event):
        execution_order.append("high")
    
    async def normal_priority_handler(event):
        execution_order.append("normal")
    
    # 订阅事件（注意顺序）
    bus.subscribe("priority.test", low_priority_handler, EventPriority.LOW)
    bus.subscribe("priority.test", normal_priority_handler, EventPriority.NORMAL)
    bus.subscribe("priority.test", high_priority_handler, EventPriority.HIGH)
    
    # 发布事件
    await bus.publish("priority.test", "测试优先级", source="test")
    
    # 验证执行顺序：高优先级先执行
    assert execution_order == ["high", "normal", "low"]
    
    await bus.stop()

@pytest.mark.asyncio
async def test_event_filter(event_bus_instance):
    """测试事件过滤器"""
    bus = event_bus_instance
    await bus.start()
    
    processed_events = []
    
    # 定义事件处理器
    async def filtered_handler(event):
        processed_events.append(event.data)
    
    # 定义过滤器函数
    def only_even_numbers(event):
        return isinstance(event.data, int) and event.data % 2 == 0
    
    # 订阅带过滤器的事件
    bus.subscribe("filter.test", filtered_handler, filter_func=only_even_numbers)
    
    # 发布多个事件
    await bus.publish("filter.test", 1, source="test")  # 应该被过滤
    await bus.publish("filter.test", 2, source="test")  # 应该被处理
    await bus.publish("filter.test", 3, source="test")  # 应该被过滤
    await bus.publish("filter.test", 4, source="test")  # 应该被处理
    
    # 验证只有偶数被处理
    assert processed_events == [2, 4]
    
    await bus.stop()

@pytest.mark.asyncio
async def test_request_response_pattern(event_bus_instance):
    """测试请求-响应模式"""
    bus = event_bus_instance
    await bus.start()
    
    # 定义服务处理器
    async def weather_service(event):
        if event.data["city"] == "北京":
            return {"temperature": 25, "condition": "晴朗"}
        return None
    
    async def default_weather_service(event):
        return {"temperature": 20, "condition": "未知"}
    
    # 订阅服务
    bus.subscribe(EventNames.WEATHER_REQUEST, weather_service)
    bus.subscribe(EventNames.WEATHER_REQUEST, default_weather_service)
    
    # 发送请求
    result = await bus.request(
        EventNames.WEATHER_REQUEST,
        {"city": "北京"},
        source="test_user"
    )
    
    # 验证结果
    assert result is not None
    assert result["temperature"] == 25
    assert result["condition"] == "晴朗"
    
    await bus.stop()

# 添加一个简单的同步测试来验证基本功能
def test_event_bus_creation():
    """测试事件总线创建"""
    bus = EventBus()
    assert bus is not None
    assert bus._handlers == {}
    assert not bus._running

def test_event_subscription():
    """测试事件订阅"""
    bus = EventBus()
    
    def simple_handler(event):
        return "handled"
    
    bus.subscribe("test.event", simple_handler)
    
    assert "test.event" in bus._handlers
    assert len(bus._handlers["test.event"]) == 1
    
    # 测试取消订阅
    bus.unsubscribe("test.event", simple_handler)
    assert len(bus._handlers["test.event"]) == 0