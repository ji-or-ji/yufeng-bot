# API 参考

## 目录

- [机器人](bot.md)
- [消息](message.md)
- [权限](permission.md)
- [插件](plugin.md)
- [定时任务](scheduler.md)
- [数据库](database.md)
- [配置](config.md)
- [日志](log.md)

## 架构概述

御风_BOT采用基于事件总线的插件化架构，所有组件（bot本体和插件）都连接到内部消息总线。系统通过权限控制机制确保插件的安全运行。

### 核心设计原则

1. **权限控制**：插件必须声明所需权限，并在配置文件中获得用户许可才能执行敏感操作
2. **消息路由**：内部消息总线负责消息的路由和分发，支持权限检查
3. **插件扩展**：插件可以扩展bot功能，包括修改AI提示词和发送外部消息
4. **直接消息发送**：**插件可以直接发送消息到消息总线**，前提是拥有相应的权限配置

### 插件消息发送权限说明

**重要特性**：插件被允许直接发送消息到消息总线，无需通过bot本体中转。权限控制机制确保只有获得用户授权的插件才能执行敏感操作：

- ✅ **内部消息总线**：所有已加载的插件都可以发送消息到内部总线
- ✅ **外部消息总线**：需要`send_external`权限，在配置文件中明确授权
- ✅ **提示词修改**：需要`modify_prompts`权限，在配置文件中明确授权
- ✅ **直接通信**：插件与bot本体、插件与插件之间可以直接通信

## 消息系统

### 消息总线架构

```text
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   插件A     │────│  内部消息总线   │────│  外部消息总线 │
├─────────────┤    ├─────────────────┤    ├─────────────┤
│   插件B     │    │  权限检查器     │    │  QQ连接器   │
├─────────────┤    ├─────────────────┤    ├─────────────┤
│   Bot本体   │    │  事件路由器     │    │  微信连接器  │
└─────────────┘    └─────────────────┘    └─────────────┘
```

### 消息发送函数

#### 基础消息发送

```python
async def send_message(source: str, address: str, message: dict) -> bool:
    """
    发送消息到指定地址，支持权限检查和消息路由
    
    参数:
        source: 消息发送者标识（bot本体或插件名称）
        address: 目标地址（"internal" 或 "external"）
        message: 消息内容字典
    
    返回:
        bool: 发送是否成功
    """
    # 权限检查
    if not await check_permission(source, address, message):
        logger.warning(f"权限检查失败: {source} 尝试发送消息到 {address}")
        return False
    
    # 消息路由
    if address == "internal":
        return await route_to_internal_bus(message)
    elif address == "external":
        return await route_to_external_bus(message)
    else:
        logger.error(f"未知的目标地址: {address}")
        return False
```

#### 插件消息发送（带权限检查）

```python
async def plugin_send_message(plugin_name: str, message: dict, target: str = "internal") -> bool:
    """
    插件专用的消息发送函数，包含完整的权限验证流程
    
    🔥 重要特性：插件可以直接发送消息到消息总线，无需通过bot本体中转！
    
    参数:
        plugin_name: 插件名称（必须与配置文件中的名称一致）
        message: 消息内容字典
        target: 目标类型（"internal" 内部总线，"external" 外部总线）
    
    返回:
        bool: 发送是否成功
    """
    # 检查插件是否已加载且具有相应权限
    plugin_config = await get_plugin_config(plugin_name)
    if not plugin_config or not plugin_config.get("enabled", False):
        logger.error(f"插件未加载或未启用: {plugin_name}")
        return False
    
    # 检查发送到外部总线的权限
    if target == "external":
        if not plugin_config.get("permissions", {}).get("send_external", False):
            logger.warning(f"插件 {plugin_name} 没有发送外部消息的权限")
            return False
    
    # 构造完整消息
    full_message = {
        "source": f"plugin:{plugin_name}",
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "data": message
    }
    
    # 🔥 插件直接发送消息到消息总线
    return await send_message(f"plugin:{plugin_name}", target, full_message)
```

#### Bot本体消息发送

```python
async def bot_send_message(message: dict, target: str = "internal") -> bool:
    """
    Bot本体专用的消息发送函数，无需权限检查
    
    参数:
        message: 消息内容字典
        target: 目标类型（"internal" 内部总线，"external" 外部总线）
    
    返回:
        bool: 发送是否成功
    """
    full_message = {
        "source": "bot:core",
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "data": message
    }
    
    return await send_message("bot:core", target, full_message)
```

### 消息格式规范

#### 基础消息格式

```python
{
    "source": "bot:core",  # 或 "plugin:插件名称"
    "timestamp": "2024-01-01T12:00:00",
    "target": "internal",  # 或 "external"
    "data": {
        "type": "text",    # 消息类型：text, image, command, event等
        "content": "消息内容",
        "metadata": {}     # 附加元数据
    }
}
```

#### 文本消息格式

```python
{
    "source": "plugin:weather",
    "timestamp": "2024-01-01T12:00:00",
    "target": "external",
    "data": {
        "type": "text",
        "content": "今天天气晴朗，温度25℃",
        "metadata": {
            "group_id": "1234567890",
            "user_id": "9876543210",
            "reply_to": "消息ID（可选）"
        }
    }
}
```

#### 命令消息格式

```python
{
    "source": "bot:core",
    "timestamp": "2024-01-01T12:00:00",
    "target": "internal",
    "data": {
        "type": "command",
        "command": "update_prompt",
        "parameters": {
            "agent": "yufeng",
            "prompt_key": "system_prompt",
            "new_prompt": "新的系统提示词内容"
        },
        "metadata": {
            "requester": "plugin:personality_manager"
        }
    }
}
```

## 权限控制系统

### 权限检查函数

```python
async def check_permission(source: str, address: str, message: dict) -> bool:
    """
    检查消息发送权限
    
    参数:
        source: 消息来源
        address: 目标地址
        message: 消息内容
    
    返回:
        bool: 是否具有权限
    """
    # Bot本体始终具有所有权限
    if source.startswith("bot:"):
        return True
    
    # 插件权限检查
    if source.startswith("plugin:"):
        plugin_name = source.replace("plugin:", "")
        return await check_plugin_permission(plugin_name, address, message)
    
    return False

async def check_plugin_permission(plugin_name: str, address: str, message: dict) -> bool:
    """
    检查插件特定权限
    
    参数:
        plugin_name: 插件名称
        address: 目标地址
        message: 消息内容
    
    返回:
        bool: 是否具有权限
    """
    plugin_config = await get_plugin_config(plugin_name)
    if not plugin_config:
        return False
    
    permissions = plugin_config.get("permissions", {})
    
    # 检查发送到外部总线的权限
    if address == "external":
        if not permissions.get("send_external", False):
            return False
    
    # 检查修改提示词的权限
    if (message.get("data", {}).get("type") == "command" and 
        message.get("data", {}).get("command") == "update_prompt"):
        if not permissions.get("modify_prompts", False):
            return False
    
    return True
```

### 插件权限配置示例

```yaml
# config/plugins/weather_plugin.yaml
plugin:
  name: "weather"
  version: "1.0.0"
  enabled: true
  permissions:
    send_external: true      # 允许发送消息到外部总线
    modify_prompts: false    # 不允许修改AI提示词
    access_database: true    # 允许访问数据库
  dependencies:
    - core
    - database
```

## 插件扩展功能

### 提示词修改功能

```python
async def update_agent_prompt(plugin_name: str, agent: str, prompt_key: str, new_prompt: str) -> bool:
    """
    插件修改AI代理提示词的函数
    
    参数:
        plugin_name: 插件名称
        agent: AI代理名称（如 "yufeng"）
        prompt_key: 提示词键名（如 "system_prompt", "personality_prompt"）
        new_prompt: 新的提示词内容
    
    返回:
        bool: 修改是否成功
    """
    # 检查权限
    if not await check_plugin_permission(plugin_name, "internal", {
        "type": "command",
        "command": "update_prompt",
        "parameters": {"agent": agent, "prompt_key": prompt_key}
    }):
        logger.warning(f"插件 {plugin_name} 没有修改提示词的权限")
        return False
    
    # 发送修改命令
    message = {
        "type": "command",
        "command": "update_prompt",
        "parameters": {
            "agent": agent,
            "prompt_key": prompt_key,
            "new_prompt": new_prompt,
            "modified_by": plugin_name
        }
    }
    
    return await plugin_send_message(plugin_name, message, "internal")
```

### 插件消息接收处理

```python
async def plugin_message_handler(plugin_name: str, message: dict):
    """
    插件消息处理函数模板
    
    参数:
        plugin_name: 插件名称
        message: 接收到的消息
    """
    try:
        message_type = message.get("data", {}).get("type")
        
        if message_type == "text":
            await handle_text_message(plugin_name, message)
        elif message_type == "command":
            await handle_command_message(plugin_name, message)
        elif message_type == "event":
            await handle_event_message(plugin_name, message)
        else:
            logger.warning(f"未知的消息类型: {message_type}")
            
    except Exception as e:
        logger.error(f"插件 {plugin_name} 消息处理错误: {e}")

async def handle_text_message(plugin_name: str, message: dict):
    """处理文本消息"""
    content = message.get("data", {}).get("content", "")
    metadata = message.get("data", {}).get("metadata", {})
    
    # 插件特定的文本消息处理逻辑
    logger.info(f"插件 {plugin_name} 收到文本消息: {content}")

async def handle_command_message(plugin_name: str, message: dict):
    """处理命令消息"""
    command = message.get("data", {}).get("command")
    parameters = message.get("data", {}).get("parameters", {})
    
    if command == "reload_config":
        await reload_plugin_config(plugin_name)
    elif command == "execute_task":
        await execute_plugin_task(plugin_name, parameters)
```

## 完整使用示例

### 插件开发示例：天气插件

```python
class WeatherPlugin:
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.initialized = False
    
    async def initialize(self):
        """插件初始化"""
        # 注册消息处理器
        await register_message_handler(self.plugin_name, self.message_handler)
        self.initialized = True
        logger.info(f"天气插件 {self.plugin_name} 初始化完成")
    
    async def message_handler(self, message: dict):
        """消息处理函数"""
        await plugin_message_handler(self.plugin_name, message)
    
    async def send_weather_report(self, location: str, group_id: str = None):
        """
        发送天气报告
        
        🔥 重要说明：插件可以直接发送消息到外部消息总线！
        前提：插件配置文件中必须设置 send_external: true 权限
        """
        # 获取天气数据
        weather_data = await self.get_weather_data(location)
        
        # 构造消息
        message = {
            "type": "text",
            "content": f"{location}的天气：{weather_data['description']}，温度{weather_data['temperature']}℃",
            "metadata": {
                "group_id": group_id
            } if group_id else {}
        }
        
        # 🔥 插件直接发送消息到外部消息总线（需要权限）
        success = await plugin_send_message(self.plugin_name, message, "external")
        
        if success:
            logger.info(f"天气插件成功发送天气报告: {location}")
        else:
            logger.error(f"天气插件发送天气报告失败: {location}")
    
    async def get_weather_data(self, location: str) -> dict:
        """获取天气数据（模拟）"""
        # 实际实现中这里会调用天气API
        return {
            "location": location,
            "temperature": 25,
            "description": "晴朗",
            "humidity": 60
        }

# 插件使用示例
async def main():
    # 创建天气插件实例
    weather_plugin = WeatherPlugin("weather")
    
    # 初始化插件
    await weather_plugin.initialize()
    
    # 🔥 插件直接发送消息到外部总线（权限足够时）
    await weather_plugin.send_weather_report("北京", "1234567890")
```

### Bot本体消息处理示例

```python
class BotCore:
    def __init__(self):
        self.plugins = {}
        self.message_handlers = {}
    
    async def initialize(self):
        """Bot本体初始化"""
        # 注册消息处理器
        await register_message_handler("bot:core", self.message_handler)
        
        # 加载插件
        await self.load_plugins()
        
        logger.info("Bot本体初始化完成")
    
    async def message_handler(self, message: dict):
        """Bot本体消息处理"""
        source = message.get("source")
        message_type = message.get("data", {}).get("type")
        
        if source.startswith("plugin:"):
            # 处理来自插件的消息
            await self.handle_plugin_message(message)
        elif message_type == "text":
            # 处理文本消息
            await self.handle_text_message(message)
    
    async def handle_plugin_message(self, message: dict):
        """处理插件消息"""
        plugin_name = message.get("source").replace("plugin:", "")
        command = message.get("data", {}).get("command")
        
        if command == "update_prompt":
            # 处理提示词更新请求
            parameters = message.get("data", {}).get("parameters", {})
            await self.update_agent_prompt(
                parameters.get("agent"),
                parameters.get("prompt_key"),
                parameters.get("new_prompt"),
                plugin_name
            )
    
    async def update_agent_prompt(self, agent: str, prompt_key: str, new_prompt: str, modified_by: str):
        """更新AI代理提示词"""
        # 实际实现中这里会更新对应的AI代理配置
        logger.info(f"更新 {agent} 的提示词 {prompt_key}，修改者: {modified_by}")
        
        # 发送确认消息回插件
        confirmation_message = {
            "type": "event",
            "event": "prompt_updated",
            "data": {
                "agent": agent,
                "prompt_key": prompt_key,
                "status": "success"
            }
        }
        
        await bot_send_message(confirmation_message, "internal")
```

## 配置说明

### 插件配置文件格式

```yaml
# config/plugins/插件名称.yaml
plugin:
  name: "插件名称"
  version: "1.0.0"
  author: "作者名称"
  description: "插件功能描述"
  enabled: true
  permissions:
    send_external: true      # 发送外部消息权限
    modify_prompts: false    # 修改提示词权限
    access_database: true    # 访问数据库权限
    read_config: true        # 读取配置权限
    write_config: false      # 写入配置权限
  dependencies:
    - core                   # 依赖的核心模块
    - database              # 依赖的数据库模块
  configuration:
    api_key: ""             # 插件配置项
    interval: 300           # 执行间隔（秒）
```

### 系统配置文件

```yaml
# config/default.yaml
system:
  event_bus:
    internal_address: "internal"
    external_address: "external"
    max_queue_size: 1000
    timeout: 30
  
  plugins:
    auto_load: true
    scan_interval: 60
    permission_strict_mode: true
  
  security:
    enable_permission_check: true
    log_permission_violations: true
```

## 总结

### 插件直接发送消息的核心特性

🔥 **关键要点**：插件可以直接发送消息到消息总线，无需通过bot本体中转！

**权限控制机制**：

- ✅ **内部消息总线**：所有已加载插件都可以直接发送消息
- ✅ **外部消息总线**：需要`send_external`权限，在配置文件中明确授权
- ✅ **提示词修改**：需要`modify_prompts`权限，在配置文件中明确授权

**设计优势**：

1. **高效通信**：插件可以直接与bot本体、其他插件和外部系统通信
2. **权限安全**：严格的权限控制确保系统安全
3. **灵活扩展**：插件可以独立实现复杂功能，无需bot本体干预
4. **松耦合架构**：插件与bot本体解耦，便于维护和扩展

这个API参考文档提供了完整的消息发送与接收机制说明，包括权限控制、插件扩展功能和实际使用示例，可以帮助您清晰地理解和实现相关功能。
