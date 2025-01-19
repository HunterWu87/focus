# RSS 翻译器

一个支持中文翻译的 RSS 阅读器，可以获取 RSS 源内容并自动将标题翻译成中文，同时提供文章总结功能。

## 功能特点

- 🌐 自动获取 RSS 源内容
- 🔄 实时翻译文章标题
- 📝 AI 生成文章总结（300-500字）
- 💾 本地数据库存储，避免重复翻译和总结
- 🎨 美观的深色主题界面
- 🖥️ 支持窗口状态记忆
- 📱 响应式布局设计

## 安装说明

1. 克隆项目：
```bash
git clone https://github.com/yourusername/rss-translator.git
cd rss-translator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 中设置你的 DeepSeek API 密钥：
```
DEEPSEEK_API_KEY=your_api_key_here
```

4. 配置 PostgreSQL：
   - 安装 PostgreSQL 数据库
   - 创建数据库用户和密码
   - 在 `src/rss_translator/database/manager.py` 中更新数据库连接参数

## 使用说明

1. 启动程序：
```bash
python main.py
```

2. 功能说明：
   - 左侧显示文章列表
   - 右侧上方显示文章总结
   - 右侧下方显示原文链接
   - 点击文章可查看 AI 生成的总结
   - 可直接在浏览器中打开原文

## 项目结构

```
rss_translator/
├── main.py                     # 主程序入口
├── requirements.txt            # 项目依赖
├── .env                       # 环境变量配置
└── src/
    └── rss_translator/        # 源代码包
        ├── __init__.py        # 包初始化文件
        ├── config.py          # 配置文件
        ├── ui.py              # 用户界面
        ├── rss_reader.py      # RSS阅读器
        ├── translator.py      # 翻译服务
        ├── utils.py           # 工具函数
        └── database/          # 数据库模块
            ├── __init__.py
            ├── manager.py     # 数据库管理
            └── models.py      # 数据模型
```

## 技术栈

- Python 3.8+
- CustomTkinter - 现代化 GUI 框架
- DeepSeek V3 - AI 翻译和总结
- PostgreSQL - 数据存储
- feedparser - RSS 解析
- requests - HTTP 请求
- beautifulsoup4 - 网页解析

## 配置选项

在 `config.py` 中可以配置以下选项：
- RSS 源地址
- 窗口默认大小
- API 请求延迟
- 数据库连接参数

## 开发计划

- [ ] 支持多 RSS 源管理
- [ ] 添加文章分类功能
- [ ] 支持自定义翻译语言
- [ ] 添加文章收藏功能
- [ ] 支持导出文章总结

## 贡献指南

欢迎提交 Pull Request 或 Issue。在提交代码前，请确保：
1. 代码符合 PEP 8 规范
2. 添加必要的注释和文档
3. 所有测试通过

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。