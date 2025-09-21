# 代码示例和建议 (Code Examples & Recommendations)

## 事件系统示例

```python
# src/yufeng_bot/core/event_bus.py
from typing import Callable, Dict, List
import asyncio

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    async def publish(self, event_type: str, data: dict):
        """发布事件到所有订阅者"""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                await callback(data)
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅特定类型的事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
```

### 配置加载器示例

```python
# src/yufeng_bot/utils/config_loader.py
import yaml
import json
from pathlib import Path
from pydantic import BaseModel
```
