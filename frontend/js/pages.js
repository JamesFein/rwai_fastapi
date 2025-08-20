// 页面内容加载模块

// 大纲生成页面
function loadOutlineGeneratePage(container) {
  container.innerHTML = `
        <div class="row">
            <!-- 操作区域 -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-file-text"></i>
                            文档上传与配置
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="outline-form">
                            <!-- 文件上传区域 -->
                            <div class="mb-4">
                                <label class="form-label">选择文档文件</label>
                                <div class="file-upload-area" id="file-drop-zone">
                                    <div class="file-upload-icon">
                                        <i class="bi bi-cloud-upload"></i>
                                    </div>
                                    <h6>拖拽文件到此处或点击选择</h6>
                                    <p class="text-muted mb-0">支持 .md 和 .txt 格式，最大 10MB</p>
                                    <input type="file" id="file-input" class="d-none" accept=".md,.txt">
                                </div>
                                <div id="file-info" class="mt-2" style="display: none;">
                                    <div class="alert alert-info">
                                        <i class="bi bi-file-earmark-text"></i>
                                        <span id="file-name"></span>
                                        <span class="badge bg-secondary ms-2" id="file-size"></span>
                                    </div>
                                </div>
                            </div>

                            <!-- 基本信息 -->
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="course-id" class="form-label">课程ID</label>
                                    <input type="text" class="form-control" id="course-id" required 
                                           placeholder="例如: CS101">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="course-material-id" class="form-label">课程材料ID</label>
                                    <input type="text" class="form-control" id="course-material-id" required 
                                           placeholder="例如: 001">
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="material-name" class="form-label">材料名称</label>
                                <input type="text" class="form-control" id="material-name" required 
                                       placeholder="例如: Python基础教程">
                            </div>

                            <!-- 高级选项 -->
                            <div class="mb-3">
                                <label for="custom-prompt" class="form-label">自定义提示词 (可选)</label>
                                <textarea class="form-control" id="custom-prompt" rows="3" 
                                          placeholder="输入自定义的大纲生成提示词..."></textarea>
                            </div>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="model-name" class="form-label">模型选择</label>
                                    <select class="form-select" id="model-name">
                                        <option value="">使用默认模型</option>
                                        <option value="gpt-4o-mini">GPT-4O Mini</option>
                                        <option value="gpt-4o">GPT-4O</option>
                                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3 d-flex align-items-end">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="include-refine" checked>
                                        <label class="form-check-label" for="include-refine">
                                            启用大纲精简处理
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <button type="submit" class="btn btn-primary w-100">
                                <i class="bi bi-gear"></i>
                                生成大纲
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- 结果展示区域 -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-list-ul"></i>
                            生成结果
                        </h5>
                    </div>
                    <div class="card-body">
                        <div id="outline-result" class="text-center text-muted">
                            <i class="bi bi-file-text" style="font-size: 3rem; opacity: 0.3;"></i>
                            <p class="mt-3">请上传文档并点击生成大纲</p>
                        </div>
                    </div>
                </div>

                <!-- 任务状态卡片 -->
                <div class="card mt-3" id="task-status-card" style="display: none;">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-clock"></i>
                            任务状态
                        </h6>
                    </div>
                    <div class="card-body">
                        <div id="task-status-content">
                            <!-- 任务状态内容 -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 初始化文件上传
  initializeOutlineFileUpload();

  // 绑定表单提交事件
  document
    .getElementById("outline-form")
    .addEventListener("submit", handleOutlineFormSubmit);
}

// 初始化大纲生成页面的文件上传
function initializeOutlineFileUpload() {
  const dropZone = document.getElementById("file-drop-zone");
  const fileInput = document.getElementById("file-input");
  const fileInfo = document.getElementById("file-info");
  const fileName = document.getElementById("file-name");
  const fileSize = document.getElementById("file-size");

  // 创建拖拽上传实例并存储到全局变量
  window.outlineFileUploader = new DragDropUploader(dropZone, fileInput, {
    onSuccess: (file) => {
      fileName.textContent = file.name;
      fileSize.textContent = formatFileSize(file.size);
      fileInfo.style.display = "block";

      // 自动填充材料名称
      const materialNameInput = document.getElementById("material-name");
      if (!materialNameInput.value) {
        const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
        materialNameInput.value = nameWithoutExt;
      }
    },
    onError: (error) => {
      showError(error);
    },
  });

  // 点击上传区域触发文件选择
  dropZone.addEventListener("click", () => {
    fileInput.click();
  });
}

// 处理大纲生成表单提交
async function handleOutlineFormSubmit(e) {
  e.preventDefault();

  // 使用上传器获取选中的文件
  const file = window.outlineFileUploader
    ? window.outlineFileUploader.getSelectedFile()
    : null;

  if (!file) {
    showError("请先选择要处理的文件");
    return;
  }

  // 收集表单数据
  const formData = new FormData();
  formData.append("file", file);
  formData.append("course_id", document.getElementById("course-id").value);
  formData.append(
    "course_material_id",
    document.getElementById("course-material-id").value
  );
  formData.append(
    "material_name",
    document.getElementById("material-name").value
  );
  formData.append(
    "include_refine",
    document.getElementById("include-refine").checked
  );

  const customPrompt = document.getElementById("custom-prompt").value;
  if (customPrompt) {
    formData.append("custom_prompt", customPrompt);
  }

  const modelName = document.getElementById("model-name").value;
  if (modelName) {
    formData.append("model_name", modelName);
  }

  try {
    showLoading();

    // 调用API生成大纲
    const response = await OutlineAPI.generateOutline(formData);

    hideLoading();

    // 显示任务状态
    showTaskStatus(response);

    // 开始轮询任务状态
    startTaskPolling(response.task_id);
  } catch (error) {
    hideLoading();
    showError("生成大纲失败: " + error.message);
  }
}

// 显示任务状态
function showTaskStatus(taskData) {
  const statusCard = document.getElementById("task-status-card");
  const statusContent = document.getElementById("task-status-content");

  statusCard.style.display = "block";

  statusContent.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span>任务ID:</span>
            <code>${taskData.task_id}</code>
        </div>
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span>状态:</span>
            <span class="status-badge status-${
              taskData.status
            }">${getStatusText(taskData.status)}</span>
        </div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span>创建时间:</span>
            <span>${formatDateTime(taskData.created_at)}</span>
        </div>
        <div class="progress">
            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
        </div>
        <small class="text-muted mt-1 d-block">正在处理中...</small>
    `;
}

// 开始任务轮询
function startTaskPolling(taskId) {
  const poller = new TaskPoller(
    OutlineAPI.getTaskStatus,
    taskId,
    updateTaskStatus,
    handleTaskComplete,
    handleTaskError
  );

  poller.start(2000); // 每2秒轮询一次
}

// 更新任务状态
function updateTaskStatus(taskData) {
  const statusContent = document.getElementById("task-status-content");
  if (!statusContent) return;

  const progressBar = statusContent.querySelector(".progress-bar");
  const statusBadge = statusContent.querySelector(".status-badge");
  const statusText = statusContent.querySelector("small");

  if (progressBar) {
    const progress =
      taskData.status === "processing"
        ? 50
        : taskData.status === "completed"
        ? 100
        : 0;
    progressBar.style.width = progress + "%";
  }

  if (statusBadge) {
    statusBadge.className = `status-badge status-${taskData.status}`;
    statusBadge.textContent = getStatusText(taskData.status);
  }

  if (statusText) {
    statusText.textContent = taskData.message || "正在处理中...";
  }
}

// 处理任务完成
function handleTaskComplete(taskData) {
  if (taskData.status === "completed") {
    showSuccess("大纲生成完成！");
    displayOutlineResult(taskData);
  } else if (taskData.status === "failed") {
    showError("大纲生成失败: " + (taskData.error_message || "未知错误"));
  }
}

// 处理任务错误
function handleTaskError(error) {
  showError("任务状态查询失败: " + error.message);
}

// 显示大纲结果
function displayOutlineResult(taskData) {
  const resultContainer = document.getElementById("outline-result");

  if (taskData.outline_content) {
    resultContainer.innerHTML = `
            <div class="text-start">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0">生成的大纲内容</h6>
                    <div>
                        <button class="btn btn-sm btn-outline-primary me-2" onclick="copyToClipboard(\`${taskData.outline_content.replace(
                          /`/g,
                          "\\`"
                        )}\`)">
                            <i class="bi bi-clipboard"></i> 复制
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="downloadOutline('${
                          taskData.original_filename
                        }', \`${taskData.outline_content.replace(
      /`/g,
      "\\`"
    )}\`)">
                            <i class="bi bi-download"></i> 下载
                        </button>
                    </div>
                </div>
                <div class="border rounded p-3" style="max-height: 400px; overflow-y: auto;">
                    ${marked.parse(taskData.outline_content)}
                </div>
                <div class="mt-3 text-muted small">
                    <div>处理时间: ${formatTime(taskData.processing_time)}</div>
                    <div>完成时间: ${formatDateTime(
                      taskData.completed_at
                    )}</div>
                </div>
            </div>
        `;
  } else {
    resultContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                任务已完成，但未获取到大纲内容
            </div>
        `;
  }
}

// 下载大纲文件
function downloadOutline(originalFilename, content) {
  const filename = originalFilename
    ? originalFilename.replace(/\.[^/.]+$/, "_outline.md")
    : "outline.md";
  downloadFile(content, filename, "text/markdown");
}

// 获取状态文本
function getStatusText(status) {
  const statusMap = {
    pending: "等待中",
    processing: "处理中",
    completed: "已完成",
    failed: "失败",
  };
  return statusMap[status] || status;
}

// 任务管理页面
function loadTaskManagementPage(container) {
  container.innerHTML = `
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="bi bi-list-task"></i>
                    任务管理
                </h5>
                <button class="btn btn-outline-primary btn-sm" onclick="refreshTaskList()">
                    <i class="bi bi-arrow-clockwise"></i> 刷新
                </button>
            </div>
            <div class="card-body">
                <div id="task-list-container">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3">正在加载任务列表...</p>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 加载任务列表
  loadTaskList();
}

// 加载任务列表
async function loadTaskList() {
  try {
    const response = await OutlineAPI.getTasks();
    displayTaskList(response.tasks);
  } catch (error) {
    document.getElementById("task-list-container").innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                加载任务列表失败: ${error.message}
            </div>
        `;
  }
}

// 显示任务列表
function displayTaskList(tasks) {
  const container = document.getElementById("task-list-container");

  if (tasks.length === 0) {
    container.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.3;"></i>
                <p class="mt-3">暂无任务记录</p>
            </div>
        `;
    return;
  }

  const tableHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>任务ID</th>
                        <th>文件名</th>
                        <th>状态</th>
                        <th>创建时间</th>
                        <th>完成时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${tasks
                      .map(
                        (task) => `
                        <tr>
                            <td><code>${task.task_id}</code></td>
                            <td>${task.original_filename || "-"}</td>
                            <td>
                                <span class="status-badge status-${
                                  task.status
                                }">
                                    ${getStatusText(task.status)}
                                </span>
                            </td>
                            <td>${
                              task.created_at
                                ? formatDateTime(task.created_at)
                                : "-"
                            }</td>
                            <td>${
                              task.completed_at
                                ? formatDateTime(task.completed_at)
                                : "-"
                            }</td>
                            <td>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteTask('${
                                  task.task_id
                                }')">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `
                      )
                      .join("")}
                </tbody>
            </table>
        </div>
    `;

  container.innerHTML = tableHTML;
}

// 刷新任务列表
function refreshTaskList() {
  document.getElementById("task-list-container").innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-3">正在刷新任务列表...</p>
        </div>
    `;
  loadTaskList();
}

// 删除任务
async function deleteTask(taskId) {
  if (!confirm("确定要删除这个任务吗？")) {
    return;
  }

  try {
    await OutlineAPI.deleteTask(taskId);
    showSuccess("任务删除成功");
    refreshTaskList();
  } catch (error) {
    showError("删除任务失败: " + error.message);
  }
}

// 性能监控页面
function loadPerformanceMonitorPage(container) {
  container.innerHTML = `
        <div class="row">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="bi bi-graph-up"></i>
                            性能指标
                        </h5>
                        <button class="btn btn-outline-primary btn-sm" onclick="refreshMetrics()">
                            <i class="bi bi-arrow-clockwise"></i> 刷新
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="metrics-container">
                            <div class="text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">加载中...</span>
                                </div>
                                <p class="mt-3">正在加载性能指标...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-info-circle"></i>
                            系统状态
                        </h6>
                    </div>
                    <div class="card-body">
                        <div id="system-info">
                            <!-- 系统信息将在这里显示 -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 加载性能指标
  loadMetrics();
}

// 加载性能指标
async function loadMetrics() {
  try {
    const response = await OutlineAPI.getMetrics();
    displayMetrics(response);
  } catch (error) {
    document.getElementById("metrics-container").innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                加载性能指标失败: ${error.message}
            </div>
        `;
  }
}

// 显示性能指标
function displayMetrics(data) {
  const container = document.getElementById("metrics-container");
  const systemInfo = document.getElementById("system-info");

  // 显示基本统计
  container.innerHTML = `
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="text-center">
                    <h3 class="text-primary">${data.active_tasks}</h3>
                    <p class="text-muted mb-0">活跃任务</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="text-center">
                    <h3 class="text-success">${data.total_tasks}</h3>
                    <p class="text-muted mb-0">总任务数</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="text-center">
                    <h3 class="text-info">${
                      data.performance_metrics
                        ? Object.keys(data.performance_metrics).length
                        : 0
                    }</h3>
                    <p class="text-muted mb-0">性能指标</p>
                </div>
            </div>
        </div>

        ${
          data.performance_metrics
            ? `
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>指标名称</th>
                            <th>数值</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(data.performance_metrics)
                          .map(
                            ([key, value]) => `
                            <tr>
                                <td>${key}</td>
                                <td>${
                                  typeof value === "number"
                                    ? value.toFixed(2)
                                    : value
                                }</td>
                            </tr>
                        `
                          )
                          .join("")}
                    </tbody>
                </table>
            </div>
        `
            : '<p class="text-muted">暂无性能指标数据</p>'
        }
    `;

  // 显示系统信息
  systemInfo.innerHTML = `
        <div class="mb-3">
            <div class="d-flex justify-content-between">
                <span>系统状态:</span>
                <span class="badge bg-${
                  AppState.systemStatus === "online" ? "success" : "danger"
                }">
                    ${AppState.systemStatus === "online" ? "在线" : "离线"}
                </span>
            </div>
        </div>
        <div class="mb-3">
            <div class="d-flex justify-content-between">
                <span>当前时间:</span>
                <span>${new Date().toLocaleString("zh-CN")}</span>
            </div>
        </div>
        <div class="mb-3">
            <div class="d-flex justify-content-between">
                <span>活跃任务:</span>
                <span class="badge bg-primary">${data.active_tasks}</span>
            </div>
        </div>
    `;
}

// 刷新性能指标
function refreshMetrics() {
  document.getElementById("metrics-container").innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-3">正在刷新性能指标...</p>
        </div>
    `;
  loadMetrics();
}

// RAG 智能问答页面
function loadRagChatPage(container) {
  container.innerHTML = `
        <div class="row">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-chat-dots"></i>
                            智能问答
                        </h5>
                    </div>
                    <div class="card-body p-0">
                        <!-- 聊天消息区域 -->
                        <div class="chat-container" id="chat-messages">
                            <div class="text-center text-muted">
                                <i class="bi bi-chat-square-dots" style="font-size: 3rem; opacity: 0.3;"></i>
                                <p class="mt-3">开始您的智能问答之旅</p>
                                <p class="small">您可以询问关于已索引文档的任何问题</p>
                            </div>
                        </div>

                        <!-- 聊天输入区域 -->
                        <div class="chat-input-container p-3">
                            <form id="chat-form">
                                <div class="input-group">
                                    <input type="text" class="form-control" id="chat-input"
                                           placeholder="输入您的问题..." required>
                                    <button class="btn btn-primary" type="submit">
                                        <i class="bi bi-send"></i>
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <!-- 设置面板 -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-gear"></i>
                            智能聊天设置
                        </h6>
                    </div>
                    <div class="card-body">
                        <!-- 会话管理 -->
                        <div class="mb-3">
                            <label for="conversation-id" class="form-label">
                                <i class="bi bi-chat-square"></i> 对话会话ID
                                <span class="text-danger">*</span>
                            </label>
                            <input type="text" class="form-control" id="conversation-id"
                                   placeholder="例如: user123_session001" required>
                            <div class="form-text">用于区分不同的对话会话，支持记忆持久化</div>
                        </div>

                        <!-- 聊天引擎类型 -->
                        <div class="mb-3">
                            <label for="chat-engine-type" class="form-label">
                                <i class="bi bi-cpu"></i> 聊天引擎类型
                                <span class="text-danger">*</span>
                            </label>
                            <select class="form-select" id="chat-engine-type" required>
                                <option value="condense_plus_context">检索增强模式 (推荐)</option>
                                <option value="simple">直接对话模式</option>
                            </select>
                            <div class="form-text" id="engine-description">
                                基于文档内容的智能问答，适合知识查询
                            </div>
                        </div>

                        <!-- 过滤设置 -->
                        <div class="mb-3">
                            <label class="form-label">
                                <i class="bi bi-funnel"></i> 检索过滤 (二选一)
                            </label>
                            <div class="row">
                                <div class="col-12 mb-2">
                                    <input type="text" class="form-control" id="course-id"
                                           placeholder="课程ID (例如: course_01)">
                                </div>
                                <div class="col-12">
                                    <input type="text" class="form-control" id="course-material-id"
                                           placeholder="课程材料ID (例如: material_001)">
                                </div>
                            </div>
                            <div class="form-text">
                                <i class="bi bi-info-circle"></i>
                                只能选择一个过滤条件，如果同时填写则优先使用课程ID
                            </div>
                        </div>

                        <!-- 高级设置 -->
                        <div class="mb-3">
                            <label for="collection-name" class="form-label">集合名称 (可选)</label>
                            <input type="text" class="form-control" id="collection-name"
                                   placeholder="默认使用配置中的集合">
                        </div>

                        <div class="d-grid gap-2">
                            <button class="btn btn-outline-secondary btn-sm" onclick="clearCurrentChat()">
                                <i class="bi bi-trash"></i> 清空当前对话
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="generateConversationId()">
                                <i class="bi bi-arrow-clockwise"></i> 生成新会话ID
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 来源信息 -->
                <div class="card" id="sources-card" style="display: none;">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-file-text"></i>
                            相关来源
                        </h6>
                    </div>
                    <div class="card-body">
                        <div id="sources-container">
                            <!-- 来源信息将在这里显示 -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 绑定聊天表单提交事件
  document
    .getElementById("chat-form")
    .addEventListener("submit", handleChatSubmit);

  // 初始化聊天记忆
  window.chatMemory = {
    messages: [],
    summary: null,
    token_count: 0,
  };
}

// 处理聊天提交
async function handleChatSubmit(e) {
  e.preventDefault();

  const chatInput = document.getElementById("chat-input");
  const question = chatInput.value.trim();

  if (!question) return;

  // 验证必填字段
  const conversationId = document
    .getElementById("conversation-id")
    .value.trim();
  const chatEngineType = document.getElementById("chat-engine-type").value;

  if (!conversationId) {
    showError("请输入对话会话ID");
    return;
  }

  if (!chatEngineType) {
    showError("请选择聊天引擎类型");
    return;
  }

  // 清空输入框
  chatInput.value = "";

  // 添加用户消息到聊天界面
  addChatMessage("user", question);

  // 显示加载状态
  const loadingId = addChatMessage("assistant", "正在思考中...", true);

  try {
    // 构建智能聊天请求
    const chatData = {
      conversation_id: conversationId,
      chat_engine_type: chatEngineType,
      question: question,
    };

    // 添加过滤参数 (course_id 和 course_material_id 二选一)
    const courseId = document.getElementById("course-id").value.trim();
    const courseMaterialId = document
      .getElementById("course-material-id")
      .value.trim();

    if (courseId) {
      chatData.course_id = courseId;
    } else if (courseMaterialId) {
      chatData.course_material_id = courseMaterialId;
    }

    // 添加可选参数
    const collectionName = document
      .getElementById("collection-name")
      .value.trim();
    if (collectionName) {
      chatData.collection_name = collectionName;
    }

    // 调用智能聊天API
    const response = await ChatAPI.chat(chatData);

    // 移除加载消息
    removeChatMessage(loadingId);

    // 添加助手回复
    addChatMessage("assistant", response.answer);

    // 显示处理信息
    if (response.filter_info) {
      addChatInfo(`过滤条件: ${response.filter_info}`);
    }
    addChatInfo(
      `引擎类型: ${
        response.chat_engine_type
      } | 处理时间: ${response.processing_time.toFixed(2)}s`
    );

    // 显示来源信息 (仅condense_plus_context模式)
    if (response.sources && response.sources.length > 0) {
      displaySources(response.sources);
    } else if (response.chat_engine_type === "condense_plus_context") {
      addChatInfo("未找到相关文档片段");
    }
  } catch (error) {
    // 移除加载消息
    removeChatMessage(loadingId);

    // 显示错误消息
    addChatMessage(
      "assistant",
      "抱歉，处理您的问题时出现了错误: " + error.message
    );
    showError("查询失败: " + error.message);
  }
}

// 添加聊天消息
function addChatMessage(role, content, isLoading = false) {
  const chatContainer = document.getElementById("chat-messages");
  const messageId =
    "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9);

  // 如果是第一条消息，清空欢迎信息
  const welcomeMsg = chatContainer.querySelector(".text-center.text-muted");
  if (welcomeMsg) {
    welcomeMsg.remove();
  }

  const messageDiv = document.createElement("div");
  messageDiv.id = messageId;
  messageDiv.className = `chat-message ${role} ${isLoading ? "loading" : ""}`;

  if (role === "assistant") {
    messageDiv.innerHTML = marked.parse(content);
  } else {
    messageDiv.textContent = content;
  }

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  return messageId;
}

// 移除聊天消息
function removeChatMessage(messageId) {
  const messageElement = document.getElementById(messageId);
  if (messageElement) {
    messageElement.remove();
  }
}

// 清空聊天
function clearChat() {
  const chatContainer = document.getElementById("chat-messages");
  chatContainer.innerHTML = `
        <div class="text-center text-muted">
            <i class="bi bi-chat-square-dots" style="font-size: 3rem; opacity: 0.3;"></i>
            <p class="mt-3">开始您的智能问答之旅</p>
            <p class="small">您可以询问关于已索引文档的任何问题</p>
        </div>
    `;

  // 重置聊天记忆
  window.chatMemory = {
    messages: [],
    summary: null,
    token_count: 0,
  };

  // 隐藏来源信息
  document.getElementById("sources-card").style.display = "none";
}

// 显示来源信息
function displaySources(sources) {
  const sourcesCard = document.getElementById("sources-card");
  const sourcesContainer = document.getElementById("sources-container");

  sourcesContainer.innerHTML = sources
    .map(
      (source, index) => `
        <div class="source-card card mb-2">
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title mb-0">${
                      source.course_material_name
                    }</h6>
                    <span class="source-score">${(source.score * 100).toFixed(
                      1
                    )}%</span>
                </div>
                <p class="card-text small text-muted mb-2">
                    课程: ${source.course_id} | 材料: ${
        source.course_material_id
      }
                </p>
                <p class="card-text small">${source.chunk_text}</p>
            </div>
        </div>
    `
    )
    .join("");

  sourcesCard.style.display = "block";
}

// 集合管理页面
function loadCollectionManagementPage(container) {
  container.innerHTML = `
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="bi bi-collection"></i>
                    集合管理
                </h5>
                <button class="btn btn-outline-primary btn-sm" onclick="refreshCollections()">
                    <i class="bi bi-arrow-clockwise"></i> 刷新
                </button>
            </div>
            <div class="card-body">
                <div id="collections-container">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-3">正在加载集合列表...</p>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 加载集合列表
  loadCollections();
}

// 加载集合列表
async function loadCollections() {
  try {
    const response = await RAGAPI.getCollections();
    displayCollections(response.collections);
  } catch (error) {
    document.getElementById("collections-container").innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                加载集合列表失败: ${error.message}
            </div>
        `;
  }
}

// 显示集合列表
function displayCollections(collections) {
  const container = document.getElementById("collections-container");

  if (collections.length === 0) {
    container.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-database" style="font-size: 3rem; opacity: 0.3;"></i>
                <p class="mt-3">暂无集合</p>
                <p class="small">请先建立文档索引</p>
            </div>
        `;
    return;
  }

  const tableHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>集合名称</th>
                        <th>文档数量</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${collections
                      .map(
                        (collection) => `
                        <tr>
                            <td>
                                <strong>${collection.name}</strong>
                            </td>
                            <td>
                                <span class="badge bg-info">${collection.vectors_count}</span>
                            </td>
                            <td>
                                <span class="badge bg-success">活跃</span>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline-info me-2" onclick="viewCollectionInfo('${collection.name}')">
                                    <i class="bi bi-info-circle"></i> 详情
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteCollection('${collection.name}')">
                                    <i class="bi bi-trash"></i> 删除
                                </button>
                            </td>
                        </tr>
                    `
                      )
                      .join("")}
                </tbody>
            </table>
        </div>
    `;

  container.innerHTML = tableHTML;
}

// 智能聊天相关辅助函数

// 添加聊天信息消息
function addChatInfo(info) {
  const chatContainer = document.getElementById("chat-messages");
  const infoDiv = document.createElement("div");
  infoDiv.className = "chat-info text-muted small text-center my-2";
  infoDiv.innerHTML = `<i class="bi bi-info-circle"></i> ${info}`;
  chatContainer.appendChild(infoDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 清空当前对话
function clearCurrentChat() {
  const chatContainer = document.getElementById("chat-messages");
  chatContainer.innerHTML = `
    <div class="text-center text-muted">
      <i class="bi bi-chat-square-dots" style="font-size: 3rem; opacity: 0.3;"></i>
      <p class="mt-3">开始您的智能问答之旅</p>
      <p class="small">您可以询问关于已索引文档的任何问题</p>
    </div>
  `;

  // 隐藏来源信息
  const sourcesCard = document.getElementById("sources-card");
  if (sourcesCard) {
    sourcesCard.style.display = "none";
  }
}

// 生成新的会话ID
function generateConversationId() {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 6);
  const conversationId = `chat_${timestamp}_${random}`;

  document.getElementById("conversation-id").value = conversationId;
  addChatInfo(`已生成新会话ID: ${conversationId}`);
}

// 监听聊天引擎类型变化
document.addEventListener("DOMContentLoaded", function () {
  // 添加引擎类型变化监听器
  const engineSelect = document.getElementById("chat-engine-type");
  if (engineSelect) {
    engineSelect.addEventListener("change", function () {
      const description = document.getElementById("engine-description");
      if (this.value === "condense_plus_context") {
        description.textContent = "基于文档内容的智能问答，适合知识查询";
      } else {
        description.textContent = "与AI直接对话，不检索文档，适合一般聊天";
      }
    });
  }

  // 添加过滤字段互斥逻辑
  const courseIdInput = document.getElementById("course-id");
  const courseMaterialIdInput = document.getElementById("course-material-id");

  if (courseIdInput && courseMaterialIdInput) {
    courseIdInput.addEventListener("input", function () {
      if (this.value.trim()) {
        courseMaterialIdInput.disabled = true;
        courseMaterialIdInput.placeholder = "已选择课程ID过滤";
      } else {
        courseMaterialIdInput.disabled = false;
        courseMaterialIdInput.placeholder = "课程材料ID (例如: material_001)";
      }
    });

    courseMaterialIdInput.addEventListener("input", function () {
      if (this.value.trim()) {
        courseIdInput.disabled = true;
        courseIdInput.placeholder = "已选择课程材料ID过滤";
      } else {
        courseIdInput.disabled = false;
        courseIdInput.placeholder = "课程ID (例如: course_01)";
      }
    });
  }
});
