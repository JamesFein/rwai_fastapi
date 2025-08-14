"""
大纲生成功能测试
"""
import pytest
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import tempfile
import os

# 设置测试环境变量
os.environ["API_KEY"] = "test-api-key"
os.environ["BASE_URL"] = "https://api.openai.com/v1"
os.environ["DEBUG"] = "true"

from app.main import app
from app.services.outline_service import outline_service
from app.schemas.outline import TaskStatus

client = TestClient(app)


class TestOutlineAPI:
    """大纲生成 API 测试类"""
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime" in data
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Backend API"
        assert "version" in data
    
    def test_upload_invalid_file_type(self):
        """测试上传不支持的文件类型"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            with open(tmp_file.name, "rb") as f:
                response = client.post(
                    "/api/v1/outline/generate",
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            os.unlink(tmp_file.name)
        
        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["detail"]
    
    def test_upload_empty_file(self):
        """测试上传空文件"""
        response = client.post(
            "/api/v1/outline/generate",
            files={"file": ("", b"", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "文件名不能为空" in response.json()["detail"]
    
    @patch('app.services.outline_service.AsyncOpenAI')
    def test_generate_outline_success(self, mock_openai):
        """测试成功生成大纲"""
        # Mock OpenAI 响应
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "## 测试标题\n### 测试子标题"
        mock_response.usage = AsyncMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 创建测试文件
        test_content = "# 测试文档\n\n这是一个测试文档的内容。"
        
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp_file:
            tmp_file.write(test_content.encode('utf-8'))
            tmp_file.flush()
            
            with open(tmp_file.name, "rb") as f:
                response = client.post(
                    "/api/v1/outline/generate",
                    files={"file": ("test.md", f, "text/markdown")},
                    data={"include_refine": "false"}
                )
            
            os.unlink(tmp_file.name)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "task_id" in data
        assert "outline_content" in data
    
    def test_get_nonexistent_task(self):
        """测试查询不存在的任务"""
        response = client.get("/api/v1/outline/task/nonexistent-task-id")
        assert response.status_code == 404
        assert "任务不存在" in response.json()["detail"]
    
    def test_list_tasks(self):
        """测试获取任务列表"""
        response = client.get("/api/v1/outline/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
    
    def test_get_metrics(self):
        """测试获取性能指标"""
        response = client.get("/api/v1/outline/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "performance_metrics" in data
        assert "active_tasks" in data
        assert "total_tasks" in data

    def test_get_outline_file_not_found_course(self):
        """测试获取不存在课程的outline文件"""
        response = client.get("/api/v1/outline/file/nonexistent_course/000001")
        assert response.status_code == 404
        assert "课程目录不存在" in response.json()["message"]

    def test_get_outline_file_not_found_material(self):
        """测试获取不存在材料的outline文件"""
        response = client.get("/api/v1/outline/file/0001/nonexistent_material")
        assert response.status_code == 404
        assert "未找到课程材料文件" in response.json()["message"]

    def test_get_outline_file_empty_params(self):
        """测试空参数"""
        response = client.get("/api/v1/outline/file/ /000001")
        assert response.status_code == 400
        assert "课程ID不能为空" in response.json()["message"]

        response = client.get("/api/v1/outline/file/0001/ ")
        assert response.status_code == 400
        assert "课程材料ID不能为空" in response.json()["message"]

    def test_get_outline_file_success(self):
        """测试成功获取outline文件"""
        # 这个测试依赖于data/outputs/outlines/0001/000001_python第八章.md文件存在
        response = client.get("/api/v1/outline/file/0001/000001")

        if response.status_code == 200:
            # 如果文件存在，验证响应结构
            data = response.json()
            assert data["success"] is True
            assert data["course_id"] == "0001"
            assert data["course_material_id"] == "000001"
            assert "file_content" in data
            assert "file_path" in data
            assert "file_size" in data
            assert "last_modified" in data
            assert data["material_name"] is not None
        else:
            # 如果文件不存在，应该返回404
            assert response.status_code == 404


class TestOutlineService:
    """大纲生成服务测试类"""
    
    @pytest.mark.asyncio
    async def test_load_prompt_template(self):
        """测试加载提示词模板"""
        # 创建临时提示词文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write("测试提示词模板: {content}")
            tmp_file.flush()
            
            # 临时替换提示词路径
            original_path = outline_service._outline_prompt_template
            outline_service._outline_prompt_template = None
            
            try:
                with patch('app.constants.paths.PROMPTS_DIR', Path(tmp_file.name).parent):
                    template = await outline_service._load_prompt_template(Path(tmp_file.name).name)
                    assert "测试提示词模板" in template
                    assert "{content}" in template
            finally:
                outline_service._outline_prompt_template = original_path
                os.unlink(tmp_file.name)
    
    @pytest.mark.asyncio
    @patch('app.services.outline_service.AsyncOpenAI')
    async def test_generate_outline_from_text(self, mock_openai):
        """测试从文本生成大纲"""
        # Mock OpenAI 响应
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "## 测试大纲\n### 测试要点1\n### 测试要点2"
        mock_response.usage = AsyncMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 测试生成大纲
        content = "这是一个测试文档的内容。"
        task_id = "test-task-id"
        
        outline, tokens = await outline_service.generate_outline_from_text(
            content=content,
            task_id=task_id,
            include_refine=False
        )
        
        assert "测试大纲" in outline
        assert tokens["total_tokens"] == 150
        assert mock_client.chat.completions.create.called


class TestFileUtils:
    """文件工具测试类"""
    
    def test_sanitize_filename(self):
        """测试文件名清理"""
        from app.utils.fileio import FileIOUtils
        
        # 测试危险字符清理
        dangerous_name = "test/file\\name:with*dangerous?chars"
        clean_name = FileIOUtils.sanitize_filename(dangerous_name)
        assert "/" not in clean_name
        assert "\\" not in clean_name
        assert ":" not in clean_name
        assert "*" not in clean_name
        assert "?" not in clean_name
    
    def test_validate_file_extension(self):
        """测试文件扩展名验证"""
        from app.utils.fileio import FileIOUtils
        
        # 测试有效扩展名
        assert FileIOUtils.validate_file_extension("test.md")
        assert FileIOUtils.validate_file_extension("test.txt")
        
        # 测试无效扩展名
        assert not FileIOUtils.validate_file_extension("test.pdf")
        assert not FileIOUtils.validate_file_extension("test.docx")


class TestIDGenerator:
    """ID生成器测试类"""
    
    def test_generate_uuid(self):
        """测试UUID生成"""
        from app.utils.idgen import IDGenerator
        
        uuid1 = IDGenerator.generate_uuid()
        uuid2 = IDGenerator.generate_uuid()
        
        assert uuid1 != uuid2
        assert len(uuid1) == 36  # UUID 标准长度
        assert "-" in uuid1
    
    def test_generate_short_id(self):
        """测试短ID生成"""
        from app.utils.idgen import IDGenerator
        
        short_id = IDGenerator.generate_short_id(8)
        assert len(short_id) == 8
        assert short_id.isalnum()
    
    def test_generate_timestamp_filename(self):
        """测试时间戳文件名生成"""
        from app.utils.idgen import FilenameGenerator
        
        original = "test_document.md"
        new_filename = FilenameGenerator.generate_timestamp_filename(original)
        
        assert new_filename.endswith(".md")
        assert "test_document" in new_filename
        assert len(new_filename.split("_")) >= 3  # timestamp_taskid_original


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
