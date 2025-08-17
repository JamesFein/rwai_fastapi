# 前后端联动方案（MVP）：基于 IndexedDB 的会话持久化与 ChatSummaryBuffer 管理

> 目标读者：产品/前端/后端工程师（MVP 阶段）。  
> 目标：**不引入后端数据库**，在浏览器 IndexedDB 中存储每个会话的聊天内容与 ChatSummaryBuffer；在聊天过程中**正确携带上下文调用 FastAPI RAG 后端**；并**每隔 30 天自动清理老旧记录**。本文仅为"实施说明录"，不包含代码。

---

## 0. 范围与原则

1. 仅覆盖前端与后端之间的**数据契约**、**数据落盘策略**与**生命周期**。
2. **存储位置**：浏览器 IndexedDB（相比 LocalStorage 有更大存储空间和更好的性能）。
3. **后端状态**：尽量无状态。后端不保存会话，仅根据请求内的上下文（ChatSummaryBuffer）完成 RAG 推理并返回。
4. **MVP 从简**：先跑通"多机、多用户、单后端域名，在浏览器做数据持久化"体验；不考虑 Cookie 登录，不考虑用户数据在后端持久化。

---

## 1. 核心概念与数据结构

### 1.1 核心概念

- **会话（Session）**：一个具有独立上下文的聊天容器，用于隔离不同场景下的对话历史和上下文状态。每个会话通过唯一的 session_id 标识，维护独立的聊天历史和 ChatSummaryBuffer，支持跨时间的断续对话。具有上下文隔离性、时间持续性、场景关联性等特征。
- **ChatSummaryBuffer**：LlamaIndex 后端生成的聊天摘要的类的实例，一个实例中包含部分聊天历史，和对一个 session 中其它聊天历史的压缩。
- **前端会话聊天历史（frontend_session_chat_history）**：前端维护的完整聊天记录，用于 UI 展示，用户能够看到自己的所有发出的问题和后端返回的所有的答案就是前端会话聊天历史。
- **访问会话（visit_session）**：用户在同一域名下的浏览器会话，用于管理垃圾清理时机。
- **会话类型（session_type）**：标识会话的业务场景类型，如针对特定课件的聊天或自由聊天等。

### 1.2 会话数据结构

每个会话必须包含以下字段：

- **session_id**：会话唯一标识（nanoid 生成）
- **session_type**：会话类型（"course_material_chat" 或 "free_chat"）
- **frontend_session_chat_history**：前端聊天历史记录数组
- **chatSummaryBuffer**：LlamaIndex 后端生成的聊天摘要缓冲区（可为空）
- **mode**：聊天模式（"query" 或 "condense_question"）
- **course_id**：课程 ID（可选）
- **course_material_id**：课程材料 ID（course_material_chat 类型必需，free_chat 类型可选）
- **created_at**：创建时间戳
- **updated_at**：最后更新时间戳
- **title**：会话标题（course_material_chat 类型基于课件名称，free_chat 类型基于首条用户消息生成）

### 1.3 会话类型定义

- **course_material_chat**：针对特定课件的聊天会话

  - 必需字段：course_material_id
  - 使用场景：学生针对特定课件进行断续的学习讨论
  - 上下文范围：限定在特定课件的知识范围内
  - RAG 检索：只检索相关课件的内容

- **free_chat**：自由聊天会话（未来扩展功能，当前不实现）
  - 可选字段：course_id、course_material_id 都可为空
  - 使用场景：不使用 RAG 检索，只在 LlamaIndex 的 query 模式下与大模型直接对话
  - 上下文范围：不涉及特定课件内容
  - RAG 检索：不使用 RAG 检索功能

---

## 2. 存储架构（IndexedDB 设计）

### 2.1 数据库设计

- **数据库名称**：`ChatSessionDB`
- **版本**：1
- **对象存储**：`sessions`
- **主键**：`session_id`
- **索引**：
  - `updated_at`：用于按时间排序和清理
  - `session_type`：用于按会话类型过滤
  - `course_id`：用于按课程过滤（可选）
  - `course_material_id`：用于按课件过滤（可选）

### 2.2 存储策略

- 不使用单独的会话索引，直接从 sessions 对象存储查询
- 每个会话作为独立记录存储，便于原子操作
- 利用 IndexedDB 的索引功能实现高效查询和排序
- 确保 course_material_id 在所有会话中的唯一性（每个课件只对应一个会话）

---

## 3. 前后端交互流程

### 3.1 完整交互流程

1. **前端发送请求**：用户输入问题后，前端收集以下数据发送给后端：

   - 用户问题（question）
   - 会话 ID（session_id）
   - 聊天模式（mode：query 或 condense_question）
   - ChatSummaryBuffer（如果存在）
   - 可选：course_id、course_material_id

2. **后端处理**：

   - 根据 mode 和 chatSummaryBuffer 创建相应的聊天引擎
   - 生成回答
   - 更新 chatSummaryBuffer
   - 返回答案（在 condense_question 模式下 response 中有引用的数据）和更新后的 chatSummaryBuffer

3. **前端处理响应**：
   - 显示答案给用户，如果有显示引用文本块的逻辑，那么也要显示。
   - 将问题和答案添加到 frontend_session_chat_history
   - 如果 chatSummaryBuffer 有更新，更新 IndexedDB 中的对应记录

### 3.2 Visit Session 管理

- **开始**：用户打开项目的第一个浏览器标签页时，建立新的 visit_session
- **垃圾清理**：在 visit_session 开始时，删除所有超过 30 天未更新的会话数据
- **结束**：用户关闭项目域的最后一个浏览器标签页时，visit_session 结束

---

## 4. 前端实现要点（Frontend）

### 4.1 IndexedDB 管理模块

- 创建 IndexedDB 数据库和对象存储
- 实现会话的 CRUD 操作
- 实现按时间排序的会话列表查询（按 updated_at 倒序显示）
- 实现按 course_material_id 查找现有会话的功能
- 实现 30 天过期数据清理
- 实现特定会话的聊天历史和 ChatSummaryBuffer 清空功能

### 4.2 会话管理模块

- 使用 nanoid 生成 session_id
- 管理当前活跃会话状态
- 处理会话创建和打开（当前只支持从课件页面创建 course_material_chat 类型）
- 实现 course_material_id 唯一性检查，如存在则跳转到现有会话
- 维护 frontend_session_chat_history

### 4.3 Visit Session 管理

- 检测浏览器标签页的打开和关闭
- 使用 localStorage 或 sessionStorage 跟踪 visit_session 状态
- 在适当时机触发垃圾清理

### 4.4 聊天界面增强

- 在现有聊天界面基础上添加会话管理功能
- 添加会话列表侧边栏（按 updated_at 倒序显示所有会话）
- 支持会话切换和历史记录加载
- 提供清空当前会话聊天记录的功能按钮
- 支持从课件页面直接创建或打开 course_material_chat 类型会话

---

## 5. 后端调整要点（Backend）

### 5.1 API 接口调整

- 修改现有 `/api/v1/rag/query` 接口，支持接收 chatSummaryBuffer
- 确保响应中包含更新后的 chatSummaryBuffer
- 保持接口向后兼容性

### 5.2 ChatSummaryBuffer 处理

- 在 RAG 查询时，如果请求包含 chatSummaryBuffer，使用它来初始化聊天引擎
- 确保 chatSummaryBuffer 的正确传递和更新
- 处理 chatSummaryBuffer 为空的情况

### 5.3 Schema 更新

- 更新 QueryRequest 模型，添加 chatSummaryBuffer 字段
- 更新 QueryResponse 模型，确保返回更新后的 chatSummaryBuffer
- 保持与现有 ChatMemory 结构的兼容性

---

## 6. 数据一致性处理

### 6.1 数据重复说明

- chatSummaryBuffer 中包含的 chat_history 与 frontend_session_chat_history 部分数据重复
- 这种重复是可接受的，因为：
  - chatSummaryBuffer 用于后端上下文理解
  - frontend_session_chat_history 用于前端 UI 展示
  - 两者服务不同目的，保持独立有利于系统稳定性

### 6.2 同步策略

- 前端负责维护两套数据的同步
- 每次收到后端响应后，同时更新两个数据结构
- 在会话加载时，确保数据一致性检查

---

## 7. 性能与容量管理

### 7.1 存储限制

- IndexedDB 通常有更大的存储空间（几 GB 级别）
- 单个会话大小控制在合理范围内
- 实现会话数量上限（如最多保留 100 个会话）

### 7.2 性能优化

- 使用 IndexedDB 的异步操作避免阻塞 UI
- 会话列表按时间倒序显示，确保用户优先看到最新对话

---

## 8. 会话清空功能设计

### 8.1 功能需求

- 用户可以清空特定会话的所有聊天历史记录
- 清空操作包括：frontend_session_chat_history 和 chatSummaryBuffer
- 保留会话的基本信息（session_id、title、created_at 等）
- 重置 updated_at 为当前时间

### 8.2 实现要点（Frontend）

- 在聊天界面提供"清空聊天记录"按钮
- 操作前显示确认对话框，防止误操作
- 清空后立即更新 UI 显示，移除所有聊天消息
- 更新 IndexedDB 中的会话记录

### 8.3 清空操作的具体行为

- 将 frontend_session_chat_history 重置为空数组
- 将 chatSummaryBuffer 重置为 null
- 更新 updated_at 时间戳
- 保持其他字段不变（session_id、session_type、title、course_id 等）

---

## 9. 错误处理与容错

### 9.1 网络错误处理

- 请求失败时保留用户输入，允许重试
- 实现离线状态检测和提示

---

## 10. 开发优先级

### 10.1 第一阶段（核心功能）

1. 实现 IndexedDB 基础操作和 course_material_id 唯一性约束
2. 修改后端 API 支持 chatSummaryBuffer
3. 实现从课件页面创建或打开会话的功能

### 10.2 第二阶段（完善功能）

1. 实现会话列表和历史记录（按时间倒序显示）
2. 添加会话清空功能
3. 添加 visit_session 管理和垃圾清理
4. 完善错误处理和用户体验

### 10.3 第三阶段（优化）

1. 性能优化和缓存策略
2. 用户界面优化
3. 测试和文档完善

---

## 11. 未来扩展计划

### 11.1 free_chat 功能扩展（当前不实现）

**功能描述：**

- 支持不基于特定课件的自由聊天功能
- 不使用 RAG 检索，直接在 LlamaIndex 的 query 模式下与大模型对话
- 用户可以进行开放式的问答和讨论

**实现要点：**

- 扩展会话创建入口，支持从主页面创建 free_chat 类型会话
- 修改后端逻辑，对 free_chat 类型的请求跳过 RAG 检索步骤
- 调整前端 UI，为 free_chat 会话提供不同的显示样式

**数据结构调整：**

- 利用现有的 session_type 字段，添加对"free_chat"值的支持
- free_chat 类型会话的 course_id 和 course_material_id 字段为空
- 保持与 course_material_chat 相同的 chatSummaryBuffer 管理机制

**注意事项：**

- 当前阶段完全不考虑此功能的实现
- 数据结构已预留相关字段，未来扩展时无需大幅修改现有代码
- 实现时需要考虑 free_chat 会话的标题生成策略（基于首条用户消息）

---

## 12. 测试策略

### 12.1 前端测试

- IndexedDB 操作的单元测试
- 会话管理功能的集成测试
- course_material_id 唯一性约束测试
- 会话清空功能测试
- 跨浏览器兼容性测试

### 12.2 后端测试

- ChatSummaryBuffer 处理的单元测试
- API 接口的集成测试
- 向后兼容性测试

### 12.3 端到端测试

- 完整聊天流程测试
- 会话持久化测试
- 垃圾清理功能测试
- 从课件页面创建会话的业务流程测试

---

## 13. 详细技术实现说明

### 13.1 前端 IndexedDB 操作接口设计

#### 数据库初始化

- 数据库名：`ChatSessionDB`
- 版本：1
- 对象存储：`sessions`，主键：`session_id`
- 索引：`updated_at`（用于排序）、`course_id`（用于过滤）

#### 核心操作方法

- `createSession(sessionData)`: 创建新会话
- `getSession(sessionId)`: 获取指定会话
- `findSessionByCourseMaterilaId(courseMaterilaId)`: 根据课件 ID 查找现有会话
- `updateSession(sessionId, updates)`: 更新会话数据
- `deleteSession(sessionId)`: 删除会话
- `clearSessionHistory(sessionId)`: 清空指定会话的聊天历史和 ChatSummaryBuffer
- `listSessions(options)`: 获取会话列表（按 updated_at 倒序排序）
- `cleanupExpiredSessions(days)`: 清理过期会话

### 13.2 前端会话数据模型

#### Session 对象结构

```
{
  session_id: string,           // nanoid 生成
  session_type: string,         // 'course_material_chat' | 'free_chat'
  title: string,                // 会话标题
  frontend_session_chat_history: [
    {
      role: 'user' | 'assistant',
      content: string,
      timestamp: number
    }
  ],
  chatSummaryBuffer: object | null,  // LlamaIndex ChatSummaryBuffer
  mode: 'query' | 'condense_question',
  course_id?: string,
  course_material_id?: string,
  created_at: number,
  updated_at: number
}
```

### 13.3 后端 Schema 调整

#### QueryRequest 扩展

- 添加 `session_id: string` 字段
- 添加 `chatSummaryBuffer: object | null` 字段
- 保持现有 `chat_memory` 字段的向后兼容性

#### QueryResponse 扩展

- 确保 `chat_memory` 字段包含更新后的 ChatSummaryBuffer
- 添加 `session_id: string` 字段用于前端会话关联

### 13.4 Visit Session 实现细节

#### 检测机制

- 使用 `window.addEventListener('beforeunload')` 检测页面关闭
- 使用 `document.addEventListener('visibilitychange')` 检测标签页切换
- 使用 localStorage 的 `storage` 事件实现跨标签页通信

#### 垃圾清理触发时机

- 新 visit_session 开始时（第一个标签页打开）
- 定期检查（可选，如每小时检查一次）
- 手动触发（用户操作或开发者工具）

---

## 14. 与现有代码的集成方案

### 14.1 前端集成点

#### 现有聊天界面改造

- 保持现有 `pages.js` 中的聊天界面布局
- 在 `handleChatSubmit` 函数中集成会话管理
- 修改 `window.chatMemory` 的使用方式，改为从 IndexedDB 加载
- 添加从课件页面创建或打开会话的入口

#### 新增模块

- `sessionManager.js`: 会话管理核心逻辑，包含 course_material_id 唯一性检查
- `indexedDBHelper.js`: IndexedDB 操作封装
- `visitSessionManager.js`: 访问会话和垃圾清理管理

### 14.2 后端集成点

#### RAG Service 调整

- 修改 `rag_service.py` 中的 `query` 方法
- 支持从请求中提取 `chatSummaryBuffer`
- 确保响应中包含更新后的 `chatSummaryBuffer`

#### API 路由调整

- 保持 `/api/v1/rag/query` 接口不变
- 扩展请求和响应模型
- 确保向后兼容性

---
