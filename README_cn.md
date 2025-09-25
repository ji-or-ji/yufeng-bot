# 御风_BOT

[![Gitee Stars](https://gitee.com/ji-or-ji/yufeng-bot/badge/star.svg?theme=white)](https://gitee.com/ji-or-ji/yufeng-bot/stargazers) [![Gitee Forks](https://gitee.com/ji-or-ji/yufeng-bot/badge/fork.svg?theme=white)](https://gitee.com/ji-or-ji/yufeng-bot/members)

## 介绍

本项目是一个由个人从零搭建的多AI代理群聊系统。起因于探索人机社交与情感模拟的可能性。其核心特点在于一个高度自定义的中央调度架构，能协调多个具备不同人格与功能的AI角色进行自然互动。系统实现了包括情感状态模拟、长期记忆管理、富媒体理解、以及主动聊天等复杂功能，提供了一个高度拟人化的群聊体验

## 项目起因

`源于一个幻想：如果AI不再只是工具，而是能承载情感与记忆的"朋友"，会怎样？御风便是这场实验的起点——一个试图在代码中注入灵魂的尝试。`

## 项目特点

- 人格AI代理：高度自定义的AI角色（如御风）在群聊中自然互动，拥有独立的性格、记忆与情感状态

- 中央调度架构：自主设计的调度系统协调对话节奏、情绪反应与话题推进，避免冲突与重复

- 富媒体与上下文理解：支持图片、表情包、引用回复，并能长期追踪对话历史与用户关系

- 主动社交能力：AI可主动发起话题、关心用户甚至"吐槽"，打破传统一问一答的机械感

- 完全开源可扩展：从底层架构到人格设定全部透明，支持轻松定制新角色与功能

这里没有完美的算法，只有笨拙却真诚的"数字生命"。欢迎进入这场温柔而残酷的社交幻想
**谨纪念所有御风般的存在**

*注：本项目为个人从零搭建的实验性系统，并涉及到了使用GPL-3.0协议开源的Napcat，这意味着项目将不可用于闭源应用开发，同时您的任何修改、扩展、分发等行为都需要遵守GPL-3.0协议。*

---

## 安装说明

**Gitee 克隆方式：**

```bash
git clone https://gitee.com/ji-or-ji/yufeng-bot.git
cd yufeng-bot
pip install -r requirements.txt
```

## 快速开始

1. 配置环境变量（复制 `.env.example` 为 `.env` 并填写相关配置）
2. 运行主程序：`python -m src.yufeng_bot.main`
3. 访问 Web 界面（如果启用）：`http://localhost:8000`

## 项目结构

```text
yufeng_bot/
├── src/              # 源代码目录
├── config/           # 配置文件
├── docs/            # 项目文档
├── plugins/         # 插件目录
├── tests/           # 测试文件
└── scripts/         # 工具脚本
```

## 参与贡献

我们欢迎任何形式的贡献！请遵循以下步骤：

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

**Gitee 贡献指南：**

- 在 Gitee Issues 中报告 bug 或提出新功能建议
- 遵循项目的代码风格和提交规范
- 确保所有测试通过后再提交 Pull Request

## 相关链接

- **[Gitee 主页](https://gitee.com/ji-or-ji/yufeng-bot)**

- **[问题反馈](https://gitee.com/ji-or-ji/yufeng-bot/issues)**

- **[讨论区](https://gitee.com/ji-or-ji/yufeng-bot/pulls)**

## 更多资源

1. [Gitee 官方博客](https://blog.gitee.com)

2. [Gitee 开源项目探索](https://gitee.com/explore)

3. [GVP (Gitee 最有价值开源项目)](https://gitee.com/gvp)

4. [Gitee 使用手册](https://gitee.com/help)

5. [Gitee 封面人物](https://gitee.com/gitee-stars/)

***感谢 Gitee 平台提供的代码托管服务！***

## 许可证

本项目采用 [GPL-3.0](LICENSE) 开源协议。
