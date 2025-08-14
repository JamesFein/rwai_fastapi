"""
路径常量定义模块
统一管理应用中使用的路径常量
"""
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
TEMP_DIR = DATA_DIR / "tmp"

# 输出子目录
OUTLINES_DIR = OUTPUTS_DIR / "outlines"
RAG_DIR = OUTPUTS_DIR / "rag"
GRAPHRAG_DIR = OUTPUTS_DIR / "graphrag"

# 脚本目录
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 测试目录
TESTS_DIR = PROJECT_ROOT / "tests"

# 应用目录
APP_DIR = PROJECT_ROOT / "app"

# 文件扩展名常量
MARKDOWN_EXTENSIONS = [".md", ".markdown"]
TEXT_EXTENSIONS = [".txt"]
ALLOWED_EXTENSIONS = MARKDOWN_EXTENSIONS + TEXT_EXTENSIONS

# 文件大小限制 (字节)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 8192  # 8KB

# API 路径前缀
API_V1_PREFIX = "/api/v1"

# 提示词相关路径
PROMPTS_DIR = APP_DIR / "prompts"
OUTLINE_PROMPT_FILE = PROMPTS_DIR / "outline_generation.txt"
REFINE_PROMPT_FILE = PROMPTS_DIR / "outline_refine.txt"


def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [
        DATA_DIR,
        UPLOADS_DIR,
        OUTPUTS_DIR,
        TEMP_DIR,
        OUTLINES_DIR,
        RAG_DIR,
        GRAPHRAG_DIR,
        PROMPTS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# 在模块导入时自动创建目录
ensure_directories()
