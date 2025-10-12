"""
御风机器人 - 主程序入口
使用模拟QQ连接器进行测试
"""
import asyncio
import logging
from src.yufeng_bot.core.event_bus import event_bus, EventNames
from src.yufeng_bot.connectors.mock_qq_connector import MockQQConnector
from src.yufeng_bot.agents.simple_agent import SimpleAgent

logger = logging.getLogger(__name__)

class YufengBot:
    """机器人主类"""
    
    def __init__(self):
        self.event_bus = event_bus
        self.connector = None
        self.agent = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """初始化所有组件"""
        logger.info("🤖 初始化御风机器人...")
        
        # 启动事件总线
        await self.event_bus.start()
        
        # 初始化简单代理
        self.agent = SimpleAgent()
        await self.agent.initialize()
        
        # 初始化模拟QQ连接器
        self.connector = MockQQConnector()
        await self.connector.initialize()
        
        logger.info("✅ 御风机器人初始化完成")
    
    async def run(self):
        """运行机器人主循环"""
        logger.info("🚀 启动御风机器人...")
        
        try:
            # 发布系统启动事件
            await self.event_bus.publish(
                EventNames.SYSTEM_STARTUP,
                {"version": "1.0.0"},
                source="main"
            )
            
            logger.info("💡 输入 'exit' 可以退出程序")
            
            # 主循环 - 等待关闭信号
            await self._shutdown_event.wait()
                
        except KeyboardInterrupt:
            logger.info("收到中断信号")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """关闭机器人"""
        logger.info("🛑 关闭御风机器人...")
        
        # 发布系统关闭事件
        await self.event_bus.publish(
            EventNames.SYSTEM_SHUTDOWN,
            {"reason": "normal"},
            source="main"
        )
        
        # 关闭组件
        if self.connector:
            await self.connector.close()
        
        if self.agent:
            await self.agent.close()
        
        # 最后关闭事件总线
        await self.event_bus.stop()
        
        logger.info("👋 御风机器人已关闭")

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    bot = YufengBot()
    
    async def run_bot():
        await bot.initialize()
        await bot.run()
    
    # 运行机器人
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")

if __name__ == "__main__":
    main()