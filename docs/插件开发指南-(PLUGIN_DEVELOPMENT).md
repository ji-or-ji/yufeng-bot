# 插件开发指南

## 概述

本指南详细介绍了御风_BOT插件系统的开发流程，包括插件结构、权限管理、消息处理和最佳实践。

## 插件基础结构

### 最小插件结构

```结构
plugins/
├── my_plugin/
│   ├── __init__.py          # 插件主文件
│   ├── plugin.yaml          # 插件配置文件
│   ├── requirements.txt     # 依赖项（可选）
│   └── README.md           # 插件说明文档
```

### 插件配置文件 (plugin.yaml)

```yaml
plugin:
  name: "my_plugin"
  version: "1.0.0"
  author: "开发者名称"
  description: "插件功能描述"
  enabled: true
  permissions:
    send_external: false     # 发送外部消息权限
    modify_prompts: false    # 修改提示词权限
    access_database: false   # 访问数据库权限
    read_config: true        # 读取配置权限
  dependencies:
    - core
  configuration:
    # 插件特定的配置项
    api_key: ""
    interval: 300
```

### 插件主文件 (__init__.py)

```python
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MyPlugin:
    """插件示例类"""
    
    def __init__(self, plugin_name: str, config: Dict[str, Any]):
        self.plugin_name = plugin_name
        self.config = config
        self.initialized = False
        self.event_bus = None
    
    async def initialize(self, event_bus) -> bool:
        """插件初始化"""
        try:
            self.event_bus = event_bus
            
            # 注册消息处理器
            await self.register_handlers()
            
            # 加载插件配置
            await self.load_configuration()
            
            self.initialized = True
            logger.info(f"插件 {self.plugin_name} 初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"插件 {self.plugin_name} 初始化失败: {e}")
            return False
    
    async def register_handlers(self):
        """注册消息处理器"""
        # 注册内部消息处理器
        await self.event_bus.register_handler(
            f"plugin.{self.plugin_name}.internal",
            self.handle_internal_message
        )
        
        # 注册命令处理器
        await self.event_bus.register_handler(
            f"plugin.{self.plugin_name}.command",
            self.handle_command_message
        )
    
    async def handle_internal_message(self, message: Dict[str, Any]):
        """处理内部消息"""
        message_type = message.get("type")
        
        if message_type == "text":
            await self.handle_text_message(message)
        elif message_type == "event":
            await self.handle_event_message(message)
        else:
            logger.warning(f"未知的消息类型: {message_type}")
    
    async def handle_command_message(self, message: Dict[str, Any]):
        """处理命令消息"""
        command = message.get("command")
        parameters = message.get("parameters", {})
        
        if command == "reload":
            await self.reload_config()
        elif command == "status":
            await self.send_status_report()
        else:
            logger.warning(f"未知的命令: {command}")
    
    async def handle_text_message(self, message: Dict[str, Any]):
        """处理文本消息"""
        content = message.get("content", "")
        metadata = message.get("metadata", {})
        
        # 插件特定的文本处理逻辑
        logger.info(f"插件 {self.plugin_name} 收到文本消息: {content}")
    
    async def handle_event_message(self, message: Dict[str, Any]):
        """处理事件消息"""
        event_type = message.get("event")
        data = message.get("data", {})
        
        if event_type == "system_startup":
            await self.on_system_startup()
        elif event_type == "system_shutdown":
            await self.on_system_shutdown()
    
    async def send_message(self, message: Dict[str, Any], target: str = "internal") -> bool:
        """发送消息（带权限检查）"""
        from src.yufeng_bot.core.plugin_system.manager import plugin_send_message
        
        return await plugin_send_message(self.plugin_name, message, target)
    
    async def update_prompt(self, agent: str, prompt_key: str, new_prompt: str) -> bool:
        """修改AI提示词（需要权限）"""
        from src.yufeng_bot.core.plugin_system.manager import update_agent_prompt
        
        return await update_agent_prompt(self.plugin_name, agent, prompt_key, new_prompt)
    
    async def load_configuration(self):
        """加载插件配置"""
        # 从配置文件加载插件特定的配置
        plugin_config = self.config.get("configuration", {})
        self.api_key = plugin_config.get("api_key", "")
        self.interval = plugin_config.get("interval", 300)
    
    async def reload_config(self):
        """重新加载配置"""
        logger.info(f"重新加载插件 {self.plugin_name} 配置")
        await self.load_configuration()
    
    async def send_status_report(self):
        """发送状态报告"""
        status_message = {
            "type": "text",
            "content": f"插件 {self.plugin_name} 运行正常",
            "metadata": {
                "plugin": self.plugin_name,
                "status": "healthy"
            }
        }
        
        await self.send_message(status_message, "internal")
    
    async def on_system_startup(self):
        """系统启动时的处理"""
        logger.info(f"插件 {self.plugin_name} 处理系统启动事件")
    
    async def on_system_shutdown(self):
        """系统关闭时的处理"""
        logger.info(f"插件 {self.plugin_name} 处理系统关闭事件")
    
    async def cleanup(self):
        """插件清理"""
        if self.event_bus:
            # 取消注册消息处理器
            await self.event_bus.unregister_handler(f"plugin.{self.plugin_name}.internal")
            await self.event_bus.unregister_handler(f"plugin.{self.plugin_name}.command")
        
        logger.info(f"插件 {self.plugin_name} 清理完成")

# 插件工厂函数
async def create_plugin(plugin_name: str, config: Dict[str, Any], event_bus) -> MyPlugin:
    """创建插件实例"""
    plugin = MyPlugin(plugin_name, config)
    success = await plugin.initialize(event_bus)
    
    if success:
        return plugin
    else:
        raise Exception(f"插件 {plugin_name} 创建失败")

# 导出插件类
__all__ = ['MyPlugin', 'create_plugin']
```

## 权限管理

### 权限类型说明

| 权限名称 | 描述 | 默认值 | 风险等级 |
|---------|------|--------|----------|
| `send_external` | 发送消息到外部总线 | false | 高 |
| `modify_prompts` | 修改AI代理提示词 | false | 高 |
| `access_database` | 访问系统数据库 | false | 中 |
| `read_config` | 读取系统配置 | true | 低 |
| `write_config` | 写入系统配置 | false | 高 |
| `execute_system` | 执行系统命令 | false | 极高 |

### 权限申请示例

```yaml
# 高权限插件配置示例
plugin:
  name: "advanced_plugin"
  permissions:
    send_external: true      # 需要用户明确授权
    modify_prompts: true     # 需要用户明确授权
    access_database: true    # 需要用户明确授权
    read_config: true        # 默认允许
    write_config: false      # 需要特殊授权

# 低权限插件配置示例  
plugin:
  name: "simple_plugin"
  permissions:
    send_external: false     # 不发送外部消息
    modify_prompts: false    # 不修改提示词
    access_database: false   # 不访问数据库
    read_config: true        # 只读取配置
```

## 消息处理模式

### 1. 请求-响应模式

```python
async def request_response_example(self):
    """请求-响应模式示例"""
    # 发送请求消息
    request_message = {
        "type": "request",
        "request_id": "unique_request_id",
        "action": "get_weather",
        "parameters": {"location": "北京"}
    }
    
    success = await self.send_message(request_message, "internal")
    
    if success:
        # 等待响应（实现超时机制）
        response = await self.wait_for_response("unique_request_id", timeout=30)
        return response
    else:
        return None

async def wait_for_response(self, request_id: str, timeout: int = 30):
    """等待响应消息"""
    # 实现响应等待逻辑
    pass
```

### 2. 发布-订阅模式

```python
async def publish_subscribe_example(self):
    """发布-订阅模式示例"""
    # 订阅特定事件
    await self.event_bus.subscribe("weather.update", self.handle_weather_update)
    
    # 发布事件
    event_message = {
        "type": "event",
        "event": "weather.update",
        "data": {
            "location": "北京",
            "temperature": 25,
            "description": "晴朗"
        }
    }
    
    await self.send_message(event_message, "internal")

async def handle_weather_update(self, event_data):
    """处理天气更新事件"""
    location = event_data.get("location")
    temperature = event_data.get("temperature")
    logger.info(f"收到天气更新: {location} {temperature}℃")
```

### 3. 命令模式

```python
async def command_pattern_example(self):
    """命令模式示例"""
    # 发送命令
    command_message = {
        "type": "command",
        "command": "update_config",
        "parameters": {
            "key": "weather_api_key",
            "value": "new_api_key_123"
        }
    }
    
    success = await self.send_message(command_message, "internal")
    
    if success:
        logger.info("配置更新命令发送成功")
    else:
        logger.error("配置更新命令发送失败")
```

## 插件生命周期管理

### 生命周期钩子

```python
class LifecyclePlugin:
    """支持完整生命周期的插件示例"""
    
    async def on_install(self):
        """插件安装时调用"""
        logger.info(f"插件 {self.plugin_name} 安装完成")
        # 执行安装逻辑，如创建数据库表等
    
    async def on_enable(self):
        """插件启用时调用"""
        logger.info(f"插件 {self.plugin_name} 已启用")
        # 执行启用逻辑，如启动定时任务等
    
    async def on_disable(self):
        """插件禁用时调用"""
        logger.info(f"插件 {self.plugin_name} 已禁用")
        # 执行禁用逻辑，如停止定时任务等
    
    async def on_uninstall(self):
        """插件卸载时调用"""
        logger.info(f"插件 {self.plugin_name} 卸载完成")
        # 执行卸载逻辑，如清理数据库表等
    
    async def on_config_change(self, new_config: Dict[str, Any]):
        """配置变更时调用"""
        logger.info(f"插件 {self.plugin_name} 配置已更新")
        self.config = new_config
        await self.load_configuration()
```

### 错误处理最佳实践

```python
class RobustPlugin:
    """具有健壮错误处理的插件"""
    
    async def safe_message_handler(self, message: Dict[str, Any]):
        """安全的消息处理器"""
        try:
            await self.handle_message(message)
        except Exception as e:
            logger.error(f"消息处理错误: {e}")
            await self.send_error_report(e, message)
    
    async def handle_message(self, message: Dict[str, Any]):
        """实际的消息处理逻辑"""
        # 实现具体的消息处理逻辑
        pass
    
    async def send_error_report(self, error: Exception, message: Dict[str, Any]):
        """发送错误报告"""
        error_message = {
            "type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "original_message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_message(error_message, "internal")
```

## 实际插件示例

### 天气插件完整实现

```python
import aiohttp
import asyncio
from datetime import datetime, timedelta

class WeatherPlugin:
    """完整的天气插件实现"""
    
    def __init__(self, plugin_name: str, config: Dict[str, Any]):
        self.plugin_name = plugin_name
        self.config = config
        self.weather_cache = {}
        self.cache_timeout = 300  # 5分钟缓存
    
    async def initialize(self, event_bus):
        """初始化天气插件"""
        self.event_bus = event_bus
        self.api_key = self.config.get("configuration", {}).get("api_key", "")
        
        # 注册定时任务
        asyncio.create_task(self.periodic_weather_update())
        
        logger.info(f"天气插件 {self.plugin_name} 初始化完成")
        return True
    
    async def periodic_weather_update(self):
        """定期天气更新"""
        while True:
            try:
                # 获取配置中的监控城市
                monitored_cities = self.config.get("configuration", {}).get("cities", [])
                
                for city in monitored_cities:
                    weather_data = await self.get_weather_data(city)
                    if weather_data:
                        await self.broadcast_weather_update(city, weather_data)
                
                # 每隔配置的间隔时间执行一次
                interval = self.config.get("configuration", {}).get("interval", 3600)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"定期天气更新错误: {e}")
                await asyncio.sleep(60)  # 错误时等待1分钟重试
    
    async def get_weather_data(self, location: str) -> Dict[str, Any]:
        """获取天气数据（带缓存）"""
        # 检查缓存
        cache_key = f"weather_{location}"
        if cache_key in self.weather_cache:
            cached_data, timestamp = self.weather_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached_data
        
        # 调用天气API
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.weather.com/v1/weather?location={location}&apikey={self.api_key}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 更新缓存
                        self.weather_cache[cache_key] = (data, datetime.now())
                        return data
                    else:
                        logger.error(f"天气API请求失败: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"获取天气数据错误: {e}")
            return None
    
    async def broadcast_weather_update(self, location: str, weather_data: Dict[str, Any]):
        """广播天气更新"""
        message = {
            "type": "event",
            "event": "weather.update",
            "data": {
                "location": location,
                "temperature": weather_data.get("temperature"),
                "description": weather_data.get("description"),
                "humidity": weather_data.get("humidity"),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await self.send_message(message, "internal")
    
    async def handle_weather_request(self, message: Dict[str, Any]):
        """处理天气查询请求"""
        location = message.get("parameters", {}).get("location")
        if not location:
            await self.send_error_response(message, "缺少位置参数")
            return
        
        weather_data = await self.get_weather_data(location)
        if weather_data:
            response = {
                "type": "response",
                "request_id": message.get("request_id"),
                "data": weather_data
            }
            await self.send_message(response, "internal")
        else:
            await self.send_error_response(message, "获取天气数据失败")
    
    async def send_error_response(self, original_message: Dict[str, Any], error_msg: str):
        """发送错误响应"""
        error_response = {
            "type": "error",
            "request_id": original_message.get("request_id"),
            "error_message": error_msg
        }
        await self.send_message(error_response, "internal")
```

## 测试和调试

### 单元测试示例

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestWeatherPlugin:
    """天气插件测试类"""
    
    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        config = {
            "plugin": {
                "name": "test_weather",
                "permissions": {"send_external": True}
            },
            "configuration": {"api_key": "test_key"}
        }
        return WeatherPlugin("test_weather", config)
    
    @pytest.mark.asyncio
    async def test_initialization(self, plugin):
        """测试插件初始化"""
        event_bus = Mock()
        event_bus.register_handler = AsyncMock()
        
        result = await plugin.initialize(event_bus)
        
        assert result is True
        assert plugin.initialized is True
    
    @pytest.mark.asyncio
    async def test_weather_data_fetch(self, plugin):
        """测试天气数据获取"""
        # 模拟API响应
        mock_response = {
            "temperature": 25,
            "description": "晴朗",
            "humidity": 60
        }
        
        # 测试缓存功能
        data = await plugin.get_weather_data("北京")
        # 验证数据格式和缓存逻辑
```

### 调试技巧

1. __日志记录__：使用结构化日志记录插件运行状态
2. __消息追踪__：为消息添加唯一ID便于追踪
3. __性能监控__：监控插件执行时间和资源使用
4. __错误报告__：实现详细的错误报告机制

## 部署和发布

### 插件打包

```bash
# 创建插件包
tar -czf my_plugin-1.0.0.tar.gz my_plugin/

# 验证
