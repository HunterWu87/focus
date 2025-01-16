# RSS阅读器

一个支持中文翻译的RSS阅读器，可以获取RSS源内容并自动将标题翻译成中文。

## 项目结构 
rss_translator/
├── main.py                     # 主程序入口
├── requirements.txt            # 项目依赖
├── .env                       # 环境变量配置
├── .gitignore                 # Git忽略文件
├── README.md                  # 项目说明
├── pyproject.toml             # 项目配置
└── src/
    └── rss_translator/        # 源代码包
        ├── __init__.py        # 包初始化文件
        ├── __main__.py        # 模块入口点
        ├── config.py          # 配置文件
        ├── rss_reader.py      # RSS阅读器
        ├── translator.py      # 翻译服务
        └── utils.py           # 工具函数