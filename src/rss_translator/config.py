"""配置文件，存储所有配置项"""
import os
from dotenv import load_dotenv
import json

# 加载.env文件中的环境变量
load_dotenv()

# 版本信息
APP_VERSION = "0.1.0"
MODEL_NAME = "deepseek-v3"  # 使用腾讯云 DeepSeek-V3 模型
MODEL_VERSION = "DeepSeek-V3"  # 671B 参数量的 MoE 模型

# API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

# DeepSeek API配置（腾讯云）
DEEPSEEK_BASE_URL = "https://api.lkeap.cloud.tencent.com/v1"

# RSS配置
DEFAULT_RSS_URL = os.getenv('RSS_URL', "http://feeds.bbci.co.uk/news/rss.xml")

# 请求配置
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '0.5'))  # API请求间隔时间（秒）

# 窗口状态配置文件路径
WINDOW_STATE_FILE = os.path.join(os.path.dirname(__file__), "window_state.json")

# 默认窗口状态
DEFAULT_WINDOW_STATE = {
    "geometry": "1200x800+100+100",  # 默认大小和位置
    "maximized": False,  # 默认不最大化
    "fullscreen": False,  # 不使用全屏模式
    "monitor": None  # 显示器信息
}

# 模型参数配置（DeepSeek-V3默认参数）
DEFAULT_TEMPERATURE = 0.7  # 默认温度系数 [0:2)
DEFAULT_TOP_P = 0.6       # 默认采样阈值
PRESENCE_PENALTY = 0.95   # 默认存在惩罚系数
MAX_TOKENS = 8000         # 最大输出长度（不含思维链长度）
MAX_INPUT_LENGTH = 56000  # 最大输入长度（64k上下文长度）

def save_window_state(*, geometry: str, maximized: bool, fullscreen: bool, monitor: dict) -> None:
    """
    保存窗口状态到配置文件
    
    Args:
        geometry: 窗口大小和位置 (格式: widthxheight+x+y)
        maximized: 是否最大化
        fullscreen: 是否全屏
        monitor: 显示器信息
    """
    try:
        state = {
            "geometry": geometry,
            "maximized": maximized,
            "fullscreen": fullscreen,
            "monitor": monitor
        }
        with open(WINDOW_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"保存窗口状态失败: {str(e)}")

def load_window_state() -> dict:
    """从配置文件加载窗口状态"""
    try:
        if os.path.exists(WINDOW_STATE_FILE):
            with open(WINDOW_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载窗口状态失败: {str(e)}")
    return DEFAULT_WINDOW_STATE.copy()  # 返回默认状态的副本 