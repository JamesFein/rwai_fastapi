# 提示词文档

本文档记录了项目中使用的所有提示词文件路径和功能说明。

## 文本生成大纲模块

### 1. 大纲生成提示词
- **文件路径**: `app/prompts/outline_generation.md`
- **功能**: 将输入的 Markdown 文档转换为二层次结构化大纲
- **输入**: 原始 Markdown 文档内容
- **输出**: 包含二级和三级标题的结构化 Markdown 大纲
- **模型**: gpt-4o-mini 或 gpt-4.1
- **来源**: 基于 `final_md2mindmap.ipynb` 中的 `text_to_raw_md_prompt_header` 和 `text_to_raw_md_prompt_footer`

### 2. 大纲精简提示词
- **文件路径**: `app/prompts/outline_refine.md`
- **功能**: 对生成的大纲进行标题精简和优化
- **输入**: 第一阶段生成的原始大纲
- **输出**: 精简后的大纲，包含合适的一级标题和简洁的二级标题
- **模型**: gpt-4o-mini
- **来源**: 基于 `final_md2mindmap.ipynb` 中的精简处理逻辑

## RAG 问答模块 (预留)

### 3. RAG 问答提示词
- **文件路径**: `app/prompts/rag_qa.md` (待实现)
- **功能**: RAG 问答系统的提示词模板
- **来源**: 基于 `LlamaIndex_ChatEngines_SharedMemory_Tutorial.ipynb`

### 4. RAG 对话总结提示词
- **文件路径**: `app/prompts/rag_summary.md` (待实现)
- **功能**: 对话历史总结的提示词模板

## GraphRAG 模块 (预留)

### 5. GraphRAG 实体提取提示词
- **文件路径**: `app/prompts/graphrag_entities.md` (待实现)
- **功能**: 从文本中提取实体和关系的提示词

### 6. GraphRAG 关系构建提示词
- **文件路径**: `app/prompts/graphrag_relations.md` (待实现)
- **功能**: 构建知识图谱关系的提示词

## 提示词使用规范

1. **文件格式**: 所有提示词文件使用 Markdown 格式
2. **参数化**: 使用 `{变量名}` 格式进行参数替换
3. **版本控制**: 提示词变更需要在此文档中记录
4. **测试**: 新提示词需要经过测试验证效果

## 更新日志

- 2024-08-14: 创建提示词文档，添加大纲生成相关提示词
