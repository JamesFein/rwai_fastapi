# 课程删除 API 重构计划

## 概述

本计划旨在重构课程删除相关的 API，删除不合理的 API 端点，创建新的规范化 API，并修复前端调用。

## 目标

1. 删除不合理的 `/api/v1/course-materials/course/${courseId}` API
2. 创建新的 `/api/v1/course/${courseId}` API 实现完整的课程删除功能
3. 修复前端调用以使用新的 API 端点

## 详细实施计划

### 第一阶段：后端 API 重构

#### 1.1 删除旧的 API 端点

**文件**: `app/api/v1/course_materials.py`

**操作**: 删除 `cleanup_course` 函数及其路由装饰器

```python
# 删除第177-216行的整个函数
@router.delete(
    "/{course_id}",
    response_model=CleanupResponse,
    summary="清理整个课程",
    description="删除整个课程的所有材料和数据，包括上传的文件、大纲、RAG索引等。删除文件的时候直接删除文件夹"
)
async def cleanup_course(...):
    # 整个函数删除
```

#### 1.2 创建新的课程 API 模块

**新建文件**: `app/api/v1/course.py`

**功能**: 创建专门的课程管理 API

```python
"""
课程管理API路由
专门处理课程级别的操作
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import shutil
from pathlib import Path

from ...core.logging import get_logger
from ...constants.paths import UPLOADS_DIR, OUTLINES_DIR
from ...repositories.rag_repository import rag_repository

logger = get_logger("course_api")
router = APIRouter(prefix="/course", tags=["课程管理"])

@router.delete("/{course_id}")
async def delete_course(course_id: str):
    """
    删除整个课程及其所有数据

    删除内容包括：
    - data/uploads/{course_id} 文件夹
    - data/outputs/outlines/{course_id} 文件夹
    - Qdrant中所有course_id匹配的向量点
    """
    # 实现详细逻辑
```

#### 1.3 实现课程删除逻辑

**核心功能**:

1. **删除上传文件夹**

   ```python
   upload_dir = UPLOADS_DIR / course_id
   if upload_dir.exists():
       shutil.rmtree(upload_dir)
   ```

2. **删除大纲文件夹**

   ```python
   outline_dir = OUTLINES_DIR / course_id
   if outline_dir.exists():
       shutil.rmtree(outline_dir)
   ```

3. **删除 Qdrant 向量数据**

   ```python
   filter_condition = {
       "must": [{"key": "course_id", "match": {"value": course_id}}]
   }
   deleted_count = await rag_repository.delete_vectors_by_filter(filter_condition)
   ```

4. **返回删除结果**
   ```python
   return {
       "success": True,
       "message": f"课程 {course_id} 删除成功",
       "course_id": course_id,
       "operations": [
           {"type": "upload_folder", "success": True, "path": str(upload_dir)},
           {"type": "outline_folder", "success": True, "path": str(outline_dir)},
           {"type": "qdrant_vectors", "success": True, "deleted_count": deleted_count}
       ]
   }
   ```

#### 1.4 注册新的路由

**文件**: `app/api/v1/__init__.py`

**修改**: 添加新的 course 路由

```python
from .course import router as course_router

# 注册路由
api_router.include_router(course_router)
```

### 第二阶段：前端修改

#### 2.1 修改 API 调用方法

**文件**: `frontend/js/api.js`

**修改**: 更新 CourseMaterialAPI 中的 cleanupCourse 方法

```javascript
// 修改第275-282行
async cleanupCourse(courseId, options = {}) {
  // 移除不必要的参数处理，新API不需要这些参数
  const url = `/api/v1/course/${courseId}`;
  return api.delete(url);
},
```

#### 2.2 查找并更新所有调用点

**需要检查的文件**:

- `frontend/` 目录下所有 HTML 文件
- `frontend/js/` 目录下所有 JavaScript 文件

**查找模式**:

```bash
grep -r "cleanupCourse\|course-materials/course" frontend/
```

**更新内容**:

- 移除传递给 `cleanupCourse` 的多余参数
- 更新任何直接调用旧 API 路径的代码

### 第三阶段：清理和优化

#### 3.1 清理 cleanup_service

**文件**: `app/services/course_material/cleanup_service.py`

**可选优化**: 由于新 API 不再使用复杂的清理服务，可以考虑：

- 保留 `cleanup_course_material` 方法（用于删除特定材料）
- 简化或移除不必要的参数和逻辑

#### 3.2 更新文档

**文件**: `README.md`

**更新内容**:

- 更新 API 文档说明
- 修正示例中的 API 调用路径
- 添加新的课程删除 API 说明

### 第四阶段：测试验证

#### 4.1 API 测试

**测试用例**:

```bash
# 测试新的课程删除API
curl -X DELETE "http://localhost:8000/api/v1/course/测试课程ID"

# 验证旧API不再存在（应该返回404）
curl -X DELETE "http://localhost:8000/api/v1/course-materials/course/测试课程ID"
```

#### 4.2 功能验证

**验证步骤**:

1. 创建测试课程数据（文件夹和 Qdrant 数据）
2. 调用新 API 删除课程
3. 验证所有相关数据被正确删除：
   - `data/uploads/测试课程ID` 文件夹不存在
   - `data/outputs/outlines/测试课程ID` 文件夹不存在
   - Qdrant 中无相关向量数据

#### 4.3 前端测试

**测试内容**:

1. 前端页面能正常调用新 API
2. 删除操作成功后前端显示正确
3. 错误处理正常工作

## 实施顺序

1. **第一步**: 创建新的 `app/api/v1/course.py` 文件
2. **第二步**: 实现课程删除逻辑
3. **第三步**: 注册新路由到 `__init__.py`
4. **第四步**: 测试新 API 功能
5. **第五步**: 修改前端 `api.js` 文件
6. **第六步**: 删除旧的 API 端点
7. **第七步**: 全面测试验证

## 风险控制

### 备份策略

- 在删除旧代码前，先确保新 API 完全正常工作
- 保留旧代码的备份，以防需要回滚

### 渐进式部署

1. 先部署新 API，保留旧 API
2. 更新前端使用新 API
3. 验证一切正常后再删除旧 API

### 错误处理

- 新 API 需要完善的错误处理和日志记录
- 确保删除操作的原子性（要么全部成功，要么全部回滚）

## 预期结果

完成后将获得：

1. **更清晰的 API 结构**: `/api/v1/course/{courseId}` 专门处理课程级操作
2. **简化的删除逻辑**: 直接使用 `shutil.rmtree()` 删除整个文件夹
3. **更好的前端体验**: 简化的 API 调用，无需复杂参数
4. **更好的可维护性**: 课程管理功能独立成模块

## 注意事项

1. **数据安全**: 删除操作不可逆，需要确保有适当的确认机制
2. **并发安全**: 考虑多用户同时操作的情况
3. **性能考虑**: 大文件夹删除可能耗时，考虑异步处理
4. **日志记录**: 详细记录删除操作，便于审计和故障排查
