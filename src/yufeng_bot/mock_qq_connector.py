"""
模拟QQ连接器 - 用于测试和开发
在没有真实QQ连接的情况下模拟消息收发
"""
import asyncio
import logging
import random
from typing import Dict, Any, List
from datetime import datetime

from src.yufeng_bot.core.event_bus import event_bus, EventNames
from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class MockQQConnector(BaseConnector):
    """
    模拟QQ连接器
    模拟用户消息和自动回复，用于开发和测试
    """
    
    def __init__(self):
        super().__init__()
        self.name = "mock_qq"
        self.version = "1.0.0"
        self._running = False
        self._message_task = None
        self._user_profiles = {}
        
        # 模拟用户数据
        self._setup_mock_users()
    
    def _setup_mock_users(self):
        """设置模拟用户"""
        self._user_profiles = {
            "user_001": {
                "nickname": "小明",
                "role": "member",
                "join_time": "2024-01-01"
            },
            "user_002": {
                "nickname": "小红", 
                "role": "admin",
                "join_time": "2024-01-02"
            },
            "user_003": {
                "nickname": "小刚",
                "role": "member",
                "join_time": "2024-01-03"
            }
        }
    
    async def initialize(self):
        """初始化连接器"""
        logger.info("初始化模拟QQ连接器...")
        
        # 订阅消息发送事件
        event_bus.subscribe(
            EventNames.MESSAGE_SENDING,
            self._handle_outgoing_message
        )
        
        # 启动模拟消息任务
        self._running = True
        self._message_task = asyncio.create_task(self._simulate_incoming_messages())
        
        logger.info("模拟QQ连接器初始化完成")
    
    async def close(self):
        """关闭连接器"""
        logger.info("关闭模拟QQ连接器...")
        self._running = False
        
        if self._message_task:
            self._message_task.cancel()
            try:
                await self._message_task
            except asyncio.CancelledError:
                pass
        
        logger.info("模拟QQ连接器已关闭")
    
    async def _handle_outgoing_message(self, event):
        """处理出站消息（发送给用户的消息）"""
        try:
            message_data = event.data
            
            # 模拟消息发送
            target = message_data.get('target', 'unknown')
            content = message_data.get('content', '')
            msg_type = message_data.get('type', 'text')
            
            if msg_type == 'text':
                logger.info(f"📤 [模拟QQ] 发送消息给 {target}: {content}")
                
                # 模拟网络延迟
                await asyncio.sleep(0.1)
                
                # 发布消息已发送事件
                await event_bus.publish(
                    EventNames.MESSAGE_SENT,
                    {
                        "target": target,
                        "content": content,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    },
                    source=self.name
                )
            else:
                logger.info(f"📤 [模拟QQ] 发送 {msg_type} 消息给 {target}")
                
        except Exception as e:
            logger.error(f"发送消息时出错: {e}")
    
    async def _simulate_incoming_messages(self):
        """模拟接收用户消息"""
        logger.info("开始模拟用户消息...")
        logger.info("输入 'exit' 退出模拟，输入 'help' 查看可用命令")
        
        # 初始延迟，让系统完全启动
        await asyncio.sleep(2)
        
        # 发送欢迎消息
        await self._send_welcome_message()
        
        while self._running:
            try:
                # 等待用户输入（模拟接收消息）
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "👤 输入模拟消息 (或输入 'help'): "
                )
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'auto':
                    await self._start_auto_mode()
                    continue
                elif user_input.lower() == '':
                    continue
                
                # 处理用户输入
                await self._process_user_input(user_input)
                
            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                logger.error(f"模拟消息循环出错: {e}")
                await asyncio.sleep(1)
    
    async def _send_welcome_message(self):
        """发送欢迎消息"""
        welcome_msg = """
🤖 宇风机器人 - 模拟QQ连接器已启动

可用命令:
• 直接输入消息内容 - 模拟用户发送消息
• 'auto' - 启动自动测试模式
• 'help' - 显示帮助信息  
• 'exit' - 退出模拟器

现在可以开始测试消息流了！
        """
        print(welcome_msg)
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🎮 模拟QQ连接器 - 帮助菜单

📝 基本用法:
  直接输入任何文本消息进行测试

🔧 特殊命令:
  help    - 显示此帮助
  exit    - 退出模拟器
  auto    - 自动测试模式

👥 模拟用户ID:
  user_001 - 小明 (普通成员)
  user_002 - 小红 (管理员) 
  user_003 - 小刚 (普通成员)

💡 提示:
  消息会通过事件总线发送给所有订阅者
  观察控制台输出可以看到完整的消息流
        """
        print(help_text)
    
    async def _process_user_input(self, user_input: str):
        """处理用户输入"""
        # 随机选择一个模拟用户
        user_id = random.choice(list(self._user_profiles.keys()))
        user_profile = self._user_profiles[user_id]
        
        # 构建消息数据
        message_data = {
            "message_id": f"mock_{int(datetime.now().timestamp()*1000)}",
            "user_id": user_id,
            "nickname": user_profile["nickname"],
            "content": user_input,
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "source": "private" if random.random() > 0.7 else "group",
            "group_id": "group_001" if random.random() > 0.7 else None
        }
        
        # 发布消息接收事件
        logger.info(f"📥 [模拟QQ] {user_profile['nickname']}({user_id}): {user_input}")
        
        await event_bus.publish(
            EventNames.MESSAGE_RECEIVED,
            message_data,
            source=self.name
        )
    
    async def _start_auto_mode(self):
        """启动自动测试模式"""
        logger.info("🚀 启动自动测试模式...")
        
        test_messages = [
            "你好",
            "今天天气怎么样？",
            "你会做什么？",
            "讲个笑话",
            "1+1等于多少？",
            "推荐一部电影",
            "你是谁？",
            "再见"
        ]
        
        for i, message in enumerate(test_messages):
            if not self._running:
                break
                
            # 随机选择用户
            user_id = random.choice(list(self._user_profiles.keys()))
            user_profile = self._user_profiles[user_id]
            
            # 构建消息
            message_data = {
                "message_id": f"auto_{i}_{int(datetime.now().timestamp()*1000)}",
                "user_id": user_id,
                "nickname": user_profile["nickname"],
                "content": message,
                "type": "text",
                "timestamp": datetime.now().isoformat(),
                "source": "private",
                "group_id": None
            }
            
            logger.info(f"📥 [自动模式] {user_profile['nickname']}: {message}")
            
            await event_bus.publish(
                EventNames.MESSAGE_RECEIVED,
                message_data,
                source=self.name
            )
            
            # 等待一段时间再发送下一条
            await asyncio.sleep(3)
        
        logger.info("✅ 自动测试模式完成")