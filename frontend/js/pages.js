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
                    ${marked.parse(taskData.outline_content, {
                      mangle: false,
                      headerIds: false,
                    })}
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

// RAG 智能问答页面 - 全新重写版本
function loadRagChatPage(container) {
  container.innerHTML = `
        <div class="row">
            <!-- 左侧：聊天界面 -->
            <div class="col-lg-8">
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="bi bi-chat-dots"></i>
                            RAG 智能问答
                        </h5>
                        <div>
                            <button class="btn btn-outline-secondary btn-sm me-2" onclick="exportChatHistory()">
                                <i class="bi bi-download"></i> 导出
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="clearChatHistory()">
                                <i class="bi bi-trash"></i> 清空
                            </button>
                        </div>
                    </div>
                    <div class="card-body p-0 d-flex flex-column" style="height: 600px;">
                        <!-- 聊天消息区域 -->
                        <div class="chat-messages-container flex-grow-1 p-3" id="chat-messages">
                            <div class="welcome-message text-center text-muted">
                                <i class="bi bi-robot" style="font-size: 4rem; opacity: 0.3;"></i>
                                <h4 class="mt-3">欢迎使用 RAG 智能问答</h4>
                                <p class="mb-2">基于您的文档内容进行智能对话</p>
                                <div class="alert alert-info text-start">
                                    <h6><i class="bi bi-lightbulb"></i> 使用提示：</h6>
                                    <ul class="mb-0 small">
                                        <li>确保已建立文档索引</li>
                                        <li>设置对话会话ID以保持上下文</li>
                                        <li>选择合适的引擎类型</li>
                                        <li>可通过课程ID或材料ID过滤检索范围</li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <!-- 聊天输入区域 -->
                        <div class="chat-input-area border-top p-3">
                            <form id="chat-form" class="d-flex gap-2">
                                <input type="text" class="form-control" id="chat-input"
                                       placeholder="输入您的问题..." required>
                                <button class="btn btn-primary" type="submit" id="send-button">
                                    <i class="bi bi-send"></i>
                                </button>
                            </form>
                            <div class="mt-2">
                                <small class="text-muted" id="chat-status">准备就绪</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧：配置面板 -->
            <div class="col-lg-4">
                <!-- 基本配置 -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-gear"></i>
                            基本配置
                        </h6>
                    </div>
                    <div class="card-body">
                        <!-- 会话ID -->
                        <div class="mb-3">
                            <label for="conversation-id" class="form-label">
                                对话会话ID <span class="text-danger">*</span>
                            </label>
                            <div class="input-group">
                                <input type="text" class="form-control" id="conversation-id"
                                       placeholder="例如: user123_session001" required>
                                <button class="btn btn-outline-secondary" type="button" onclick="generateConversationId()">
                                    <i class="bi bi-arrow-clockwise"></i>
                                </button>
                            </div>
                            <div class="form-text">用于区分不同的对话会话</div>
                        </div>

                        <!-- 引擎类型 -->
                        <div class="mb-3">
                            <label for="chat-engine-type" class="form-label">
                                聊天引擎类型 <span class="text-danger">*</span>
                            </label>
                            <select class="form-select" id="chat-engine-type" required onchange="updateEngineDescription()">
                                <option value="condense_plus_context">检索增强模式 (推荐)</option>
                                <option value="simple">直接对话模式</option>
                            </select>
                            <div class="form-text" id="engine-description">
                                基于文档内容的智能问答，适合知识查询
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 过滤配置 -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-funnel"></i>
                            检索过滤
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="rag-course-id" class="form-label">课程ID</label>
                            <input type="text" class="form-control" id="rag-course-id"
                                   placeholder="例如: python_course">
                            <div class="form-text">按课程过滤检索结果</div>
                        </div>

                        <div class="mb-3">
                            <label for="rag-course-material-id" class="form-label">课程材料ID</label>
                            <input type="text" class="form-control" id="rag-course-material-id"
                                   placeholder="例如: chapter_01">
                            <div class="form-text">按具体材料过滤检索结果</div>
                        </div>

                        <div class="mb-3">
                            <label for="rag-collection-name" class="form-label">集合名称</label>
                            <input type="text" class="form-control" id="rag-collection-name"
                                   placeholder="默认使用配置中的集合">
                            <div class="form-text">指定向量数据库集合</div>
                        </div>

                        <div class="alert alert-warning small">
                            <i class="bi bi-info-circle"></i>
                            如果同时填写课程ID和材料ID，将优先使用课程ID进行过滤
                        </div>
                    </div>
                </div>

                <!-- 快速操作 -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-lightning"></i>
                            快速操作
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="testConnection()">
                                <i class="bi bi-wifi"></i> 测试连接
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="loadPresetConfig()">
                                <i class="bi bi-bookmark"></i> 加载预设
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="saveCurrentConfig()">
                                <i class="bi bi-save"></i> 保存配置
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" onclick="clearAllInputs()">
                                <i class="bi bi-eraser"></i> 清空配置
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 参数测试面板 -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="bi bi-code-square"></i>
                            API 参数测试
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <button class="btn btn-outline-warning btn-sm w-100" onclick="showPayloadPreview()">
                                <i class="bi bi-eye"></i> 预览请求参数
                            </button>
                        </div>
                        <div class="mb-3">
                            <button class="btn btn-outline-danger btn-sm w-100" onclick="sendRawRequest()">
                                <i class="bi bi-send"></i> 发送原始请求
                            </button>
                        </div>
                        <div class="mb-3">
                            <button class="btn btn-outline-dark btn-sm w-100" onclick="showApiDocumentation()">
                                <i class="bi bi-book"></i> API 文档
                            </button>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="debug-mode">
                            <label class="form-check-label" for="debug-mode">
                                调试模式
                            </label>
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

  // 初始化页面
  initializeRagChatPage();
}

// 初始化RAG聊天页面
function initializeRagChatPage() {
  // 绑定聊天表单提交事件
  document
    .getElementById("chat-form")
    .addEventListener("submit", handleNewChatSubmit);

  // 生成默认会话ID
  generateConversationId();

  // 设置引擎类型描述更新
  updateEngineDescription();

  // 初始化聊天状态
  window.ragChatState = {
    isProcessing: false,
    messageCount: 0,
    currentConversationId: null,
  };

  console.log("RAG聊天页面初始化完成");
}

// 处理聊天提交 - 全新重写版本
async function handleNewChatSubmit(e) {
  e.preventDefault();

  const chatInput = document.getElementById("chat-input");
  const sendButton = document.getElementById("send-button");
  const chatStatus = document.getElementById("chat-status");
  const question = chatInput.value.trim();

  if (!question) return;

  // 防止重复提交
  if (window.ragChatState.isProcessing) {
    showError("正在处理中，请稍候...");
    return;
  }

  try {
    // 设置处理状态
    window.ragChatState.isProcessing = true;
    sendButton.disabled = true;
    chatStatus.textContent = "正在发送...";

    // 收集表单数据
    const formData = {
      conversation_id: document.getElementById("conversation-id").value.trim(),
      question: question,
      chat_engine_type: document.getElementById("chat-engine-type").value,
      course_id: document.getElementById("rag-course-id").value.trim(),
      course_material_id: document
        .getElementById("rag-course-material-id")
        .value.trim(),
      collection_name: document
        .getElementById("rag-collection-name")
        .value.trim(),
    };

    // 验证必填字段
    const validationErrors = ChatAPI.validateChatRequest(formData);
    if (validationErrors.length > 0) {
      showError("参数验证失败：\n" + validationErrors.join("\n"));
      return;
    }

    // 构建API请求数据
    const chatData = ChatAPI.buildChatRequest(formData);

    console.log("发送聊天请求:", chatData);

    // 清空输入框
    chatInput.value = "";

    // 添加用户消息到聊天界面
    addNewChatMessage("user", question);

    // 显示加载状态
    const loadingId = addNewChatMessage("assistant", "🤔 正在思考中...", true);
    chatStatus.textContent = "AI正在思考...";

    // 调用智能聊天API
    const response = await ChatAPI.chat(chatData);

    // 移除加载消息
    removeNewChatMessage(loadingId);

    // 添加助手回复
    addNewChatMessage("assistant", response.answer);

    // 显示处理信息
    addChatMetaInfo(response);

    // 显示来源信息 (仅condense_plus_context模式)
    if (response.sources && response.sources.length > 0) {
      displayNewSources(response.sources);
    } else if (response.chat_engine_type === "condense_plus_context") {
      addChatSystemInfo("未找到相关文档片段");
    }

    // 更新状态
    window.ragChatState.messageCount++;
    window.ragChatState.currentConversationId = formData.conversation_id;
    chatStatus.textContent = `对话进行中 (${window.ragChatState.messageCount} 条消息)`;
  } catch (error) {
    console.error("聊天请求失败:", error);

    // 移除可能存在的加载消息
    const loadingMessages = document.querySelectorAll(".chat-message.loading");
    loadingMessages.forEach((msg) => msg.remove());

    // 显示错误消息
    addNewChatMessage(
      "assistant",
      `❌ 抱歉，处理您的问题时出现了错误：\n\n${error.message}`
    );
    showError("聊天失败: " + error.message);
    chatStatus.textContent = "发送失败";
  } finally {
    // 恢复界面状态
    window.ragChatState.isProcessing = false;
    sendButton.disabled = false;
    chatInput.focus();

    if (
      chatStatus.textContent === "正在发送..." ||
      chatStatus.textContent === "AI正在思考..." ||
      chatStatus.textContent === "发送失败"
    ) {
      chatStatus.textContent = "准备就绪";
    }
  }
}

// 新的聊天消息处理函数
function addNewChatMessage(role, content, isLoading = false) {
  const chatContainer = document.getElementById("chat-messages");
  const messageId =
    "msg-" + Date.now() + "-" + Math.random().toString(36).substring(2, 9);

  // 如果是第一条消息，清空欢迎信息
  const welcomeMsg = chatContainer.querySelector(".welcome-message");
  if (welcomeMsg) {
    welcomeMsg.remove();
  }

  const messageDiv = document.createElement("div");
  messageDiv.id = messageId;
  messageDiv.className = `chat-message-new ${role} ${
    isLoading ? "loading" : ""
  }`;

  // 创建消息内容
  const messageContent = document.createElement("div");
  messageContent.className = "message-content";

  if (role === "assistant") {
    // 使用marked解析Markdown，禁用deprecated选项
    messageContent.innerHTML = marked.parse(content, {
      mangle: false,
      headerIds: false,
    });
  } else {
    messageContent.textContent = content;
  }

  // 添加时间戳
  const timestamp = document.createElement("div");
  timestamp.className = "message-timestamp";
  timestamp.textContent = new Date().toLocaleTimeString();

  messageDiv.appendChild(messageContent);
  messageDiv.appendChild(timestamp);

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  return messageId;
}

// 移除聊天消息
function removeNewChatMessage(messageId) {
  const messageElement = document.getElementById(messageId);
  if (messageElement) {
    messageElement.remove();
  }
}

// 添加聊天元信息
function addChatMetaInfo(response) {
  const chatContainer = document.getElementById("chat-messages");
  const metaDiv = document.createElement("div");
  metaDiv.className = "chat-meta-info";

  const metaContent = [];

  if (response.filter_info) {
    metaContent.push(`🔍 过滤条件: ${response.filter_info}`);
  }

  metaContent.push(`⚙️ 引擎: ${response.chat_engine_type}`);
  metaContent.push(`⏱️ 处理时间: ${response.processing_time.toFixed(2)}s`);

  metaDiv.innerHTML = metaContent.join(" | ");

  chatContainer.appendChild(metaDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 添加系统信息
function addChatSystemInfo(info) {
  const chatContainer = document.getElementById("chat-messages");
  const systemDiv = document.createElement("div");
  systemDiv.className = "chat-system-info";
  systemDiv.innerHTML = `<i class="bi bi-info-circle"></i> ${info}`;

  chatContainer.appendChild(systemDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
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

// 新的来源信息显示函数
function displayNewSources(sources) {
  const sourcesCard = document.getElementById("sources-card");
  const sourcesContainer = document.getElementById("sources-container");

  sourcesContainer.innerHTML = sources
    .map(
      (source) => `
        <div class="source-card-new mb-3">
            <div class="source-header d-flex justify-content-between align-items-center mb-2">
                <h6 class="source-title mb-0">材料 ${
                  source.course_material_id
                }</h6>
                <span class="source-score badge bg-primary text-white">${(
                  source.score * 100
                ).toFixed(1)}%</span>
            </div>
            <div class="source-meta text-muted small mb-2">
                <i class="bi bi-book"></i> 课程: ${source.course_id} |
                <i class="bi bi-file-text"></i> 材料: ${
                  source.course_material_id
                }
            </div>
            <div class="source-content">
                <p class="mb-0">${source.chunk_text}</p>
            </div>
        </div>
    `
    )
    .join("");

  sourcesCard.style.display = "block";
}

// 更新引擎类型描述
function updateEngineDescription() {
  const engineType = document.getElementById("chat-engine-type").value;
  const description = document.getElementById("engine-description");

  if (engineType === "condense_plus_context") {
    description.textContent = "基于文档内容的智能问答，适合知识查询";
  } else if (engineType === "simple") {
    description.textContent = "直接与AI对话，不检索文档内容";
  }
}

// 清空聊天历史
function clearChatHistory() {
  if (!confirm("确定要清空所有聊天记录吗？")) {
    return;
  }

  const chatContainer = document.getElementById("chat-messages");
  chatContainer.innerHTML = `
    <div class="welcome-message text-center text-muted">
      <i class="bi bi-robot" style="font-size: 4rem; opacity: 0.3;"></i>
      <h4 class="mt-3">欢迎使用 RAG 智能问答</h4>
      <p class="mb-2">基于您的文档内容进行智能对话</p>
      <div class="alert alert-info text-start">
        <h6><i class="bi bi-lightbulb"></i> 使用提示：</h6>
        <ul class="mb-0 small">
          <li>确保已建立文档索引</li>
          <li>设置对话会话ID以保持上下文</li>
          <li>选择合适的引擎类型</li>
          <li>可通过课程ID或材料ID过滤检索范围</li>
        </ul>
      </div>
    </div>
  `;

  // 隐藏来源信息
  document.getElementById("sources-card").style.display = "none";

  // 重置状态
  window.ragChatState.messageCount = 0;
  document.getElementById("chat-status").textContent = "准备就绪";

  showSuccess("聊天记录已清空");
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
    const collections = await RAGAPI.getCollections();
    displayCollections(collections);
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
  const random = Math.random().toString(36).substring(2, 8);
  const conversationId = `chat_${timestamp}_${random}`;

  document.getElementById("conversation-id").value = conversationId;

  // 如果聊天容器存在，显示提示
  const chatContainer = document.getElementById("chat-messages");
  if (chatContainer) {
    addChatSystemInfo(`已生成新会话ID: ${conversationId}`);
  }
}

// 导出聊天历史
function exportChatHistory() {
  const chatContainer = document.getElementById("chat-messages");
  const messages = chatContainer.querySelectorAll(".chat-message-new");

  if (messages.length === 0) {
    showError("没有聊天记录可导出");
    return;
  }

  let exportContent = "# RAG 聊天记录导出\n\n";
  exportContent += `导出时间: ${new Date().toLocaleString()}\n`;
  exportContent += `会话ID: ${
    document.getElementById("conversation-id").value
  }\n\n`;

  messages.forEach((message) => {
    const role = message.classList.contains("user") ? "用户" : "AI助手";
    const content = message.querySelector(".message-content").textContent;
    const timestamp = message.querySelector(".message-timestamp").textContent;

    exportContent += `## ${role} (${timestamp})\n\n${content}\n\n`;
  });

  // 下载文件
  const blob = new Blob([exportContent], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `rag_chat_${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);

  showSuccess("聊天记录已导出");
}

// 测试连接
async function testConnection() {
  try {
    showLoading();
    const response = await ChatAPI.getHealth();
    hideLoading();

    if (response.status === "healthy") {
      showSuccess("连接测试成功！服务正常运行");
    } else {
      showError("服务状态异常: " + JSON.stringify(response));
    }
  } catch (error) {
    hideLoading();
    showError("连接测试失败: " + error.message);
  }
}

// 加载预设配置
function loadPresetConfig() {
  const presets = [
    {
      name: "Python课程问答",
      conversation_id: "python_course_chat",
      chat_engine_type: "condense_plus_context",
      course_id: "python_course",
      course_material_id: "",
      collection_name: "",
    },
    {
      name: "通用文档问答",
      conversation_id: "general_doc_chat",
      chat_engine_type: "condense_plus_context",
      course_id: "",
      course_material_id: "",
      collection_name: "",
    },
    {
      name: "简单对话模式",
      conversation_id: "simple_chat",
      chat_engine_type: "simple",
      course_id: "",
      course_material_id: "",
      collection_name: "",
    },
  ];

  const presetHtml = presets
    .map(
      (preset, index) =>
        `<button class="btn btn-outline-secondary btn-sm w-100 mb-2" onclick="applyPreset(${index})">
      ${preset.name}
    </button>`
    )
    .join("");

  const modal = document.createElement("div");
  modal.innerHTML = `
    <div class="modal fade" id="presetModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">选择预设配置</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            ${presetHtml}
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  const modalInstance = new bootstrap.Modal(
    modal.querySelector("#presetModal")
  );
  modalInstance.show();

  // 存储预设数据到全局变量
  window.chatPresets = presets;
}

// 应用预设配置
function applyPreset(index) {
  const preset = window.chatPresets[index];

  document.getElementById("conversation-id").value = preset.conversation_id;
  document.getElementById("chat-engine-type").value = preset.chat_engine_type;
  document.getElementById("rag-course-id").value = preset.course_id;
  document.getElementById("rag-course-material-id").value =
    preset.course_material_id;
  document.getElementById("rag-collection-name").value = preset.collection_name;

  updateEngineDescription();

  // 关闭模态框
  const modal = bootstrap.Modal.getInstance(
    document.getElementById("presetModal")
  );
  modal.hide();

  showSuccess(`已应用预设配置: ${preset.name}`);
}

// 保存当前配置
function saveCurrentConfig() {
  const config = {
    conversation_id: document.getElementById("conversation-id").value,
    chat_engine_type: document.getElementById("chat-engine-type").value,
    course_id: document.getElementById("rag-course-id").value,
    course_material_id: document.getElementById("rag-course-material-id").value,
    collection_name: document.getElementById("rag-collection-name").value,
    timestamp: new Date().toISOString(),
  };

  localStorage.setItem("rag_chat_config", JSON.stringify(config));
  showSuccess("配置已保存到本地存储");
}

// 清空所有输入
function clearAllInputs() {
  if (!confirm("确定要清空所有配置吗？")) {
    return;
  }

  document.getElementById("conversation-id").value = "";
  document.getElementById("chat-engine-type").value = "condense_plus_context";
  document.getElementById("rag-course-id").value = "";
  document.getElementById("rag-course-material-id").value = "";
  document.getElementById("rag-collection-name").value = "";

  updateEngineDescription();
  generateConversationId();

  showSuccess("配置已清空");
}

// 参数测试相关函数

// 预览请求参数
function showPayloadPreview() {
  const formData = {
    conversation_id: document.getElementById("conversation-id").value.trim(),
    question: "这是一个测试问题",
    chat_engine_type: document.getElementById("chat-engine-type").value,
    course_id: document.getElementById("rag-course-id").value.trim(),
    course_material_id: document
      .getElementById("rag-course-material-id")
      .value.trim(),
    collection_name: document
      .getElementById("rag-collection-name")
      .value.trim(),
  };

  const chatData = ChatAPI.buildChatRequest(formData);

  const modal = document.createElement("div");
  modal.innerHTML = `
    <div class="modal fade" id="payloadModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-code-square"></i> 请求参数预览
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">API 端点:</label>
              <code class="d-block p-2 bg-light rounded">POST /api/v1/conversation/chat</code>
            </div>
            <div class="mb-3">
              <label class="form-label">请求头:</label>
              <pre class="bg-light p-3 rounded"><code>{
  "Content-Type": "application/json"
}</code></pre>
            </div>
            <div class="mb-3">
              <label class="form-label">请求体:</label>
              <pre class="bg-light p-3 rounded"><code>${JSON.stringify(
                chatData,
                null,
                2
              )}</code></pre>
            </div>
            <div class="alert alert-info">
              <i class="bi bi-info-circle"></i>
              这是根据当前配置生成的请求参数。您可以复制这些参数用于其他工具测试。
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" onclick="copyPayloadToClipboard('${JSON.stringify(
              chatData
            ).replace(/"/g, '\\"')}')">
              <i class="bi bi-clipboard"></i> 复制参数
            </button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  const modalInstance = new bootstrap.Modal(
    modal.querySelector("#payloadModal")
  );
  modalInstance.show();
}

// 发送原始请求
async function sendRawRequest() {
  const formData = {
    conversation_id: document.getElementById("conversation-id").value.trim(),
    question: prompt("请输入测试问题:", "什么是Python？"),
    chat_engine_type: document.getElementById("chat-engine-type").value,
    course_id: document.getElementById("rag-course-id").value.trim(),
    course_material_id: document
      .getElementById("rag-course-material-id")
      .value.trim(),
    collection_name: document
      .getElementById("rag-collection-name")
      .value.trim(),
  };

  if (!formData.question) {
    showError("测试问题不能为空");
    return;
  }

  const validationErrors = ChatAPI.validateChatRequest(formData);
  if (validationErrors.length > 0) {
    showError("参数验证失败：\n" + validationErrors.join("\n"));
    return;
  }

  const chatData = ChatAPI.buildChatRequest(formData);
  const debugMode = document.getElementById("debug-mode").checked;

  try {
    showLoading();

    if (debugMode) {
      console.log("发送原始请求:", chatData);
    }

    const startTime = Date.now();
    const response = await ChatAPI.chat(chatData);
    const endTime = Date.now();

    hideLoading();

    // 显示结果模态框
    const modal = document.createElement("div");
    modal.innerHTML = `
      <div class="modal fade" id="responseModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-check-circle text-success"></i> API 响应结果
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col-md-6">
                  <h6>请求信息:</h6>
                  <pre class="bg-light p-3 rounded small"><code>${JSON.stringify(
                    chatData,
                    null,
                    2
                  )}</code></pre>
                </div>
                <div class="col-md-6">
                  <h6>响应信息:</h6>
                  <pre class="bg-light p-3 rounded small"><code>${JSON.stringify(
                    response,
                    null,
                    2
                  )}</code></pre>
                </div>
              </div>
              <div class="mt-3">
                <h6>性能信息:</h6>
                <ul class="list-unstyled">
                  <li><strong>客户端耗时:</strong> ${endTime - startTime}ms</li>
                  <li><strong>服务端处理时间:</strong> ${
                    response.processing_time
                      ? (response.processing_time * 1000).toFixed(2) + "ms"
                      : "未知"
                  }</li>
                  <li><strong>引擎类型:</strong> ${
                    response.chat_engine_type
                  }</li>
                  <li><strong>来源数量:</strong> ${
                    response.sources ? response.sources.length : 0
                  }</li>
                </ul>
              </div>
              ${
                response.answer
                  ? `
                <div class="mt-3">
                  <h6>AI 回答:</h6>
                  <div class="border p-3 rounded">${marked.parse(
                    response.answer,
                    { mangle: false, headerIds: false }
                  )}</div>
                </div>
              `
                  : ""
              }
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline-primary" onclick="copyResponseToClipboard('${JSON.stringify(
                response
              ).replace(/"/g, '\\"')}')">
                <i class="bi bi-clipboard"></i> 复制响应
              </button>
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    const modalInstance = new bootstrap.Modal(
      modal.querySelector("#responseModal")
    );
    modalInstance.show();

    if (debugMode) {
      console.log("API响应:", response);
      console.log("客户端耗时:", endTime - startTime, "ms");
    }
  } catch (error) {
    hideLoading();

    const modal = document.createElement("div");
    modal.innerHTML = `
      <div class="modal fade" id="errorModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-exclamation-triangle text-danger"></i> API 请求失败
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <h6>错误信息:</h6>
                <div class="alert alert-danger">${error.message}</div>
              </div>
              <div class="mb-3">
                <h6>请求参数:</h6>
                <pre class="bg-light p-3 rounded"><code>${JSON.stringify(
                  chatData,
                  null,
                  2
                )}</code></pre>
              </div>
              <div class="alert alert-info">
                <i class="bi bi-lightbulb"></i>
                <strong>调试建议:</strong>
                <ul class="mb-0 mt-2">
                  <li>检查API服务是否正常运行</li>
                  <li>验证所有必填参数是否正确</li>
                  <li>确认网络连接正常</li>
                  <li>查看浏览器控制台获取更多信息</li>
                </ul>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    const modalInstance = new bootstrap.Modal(
      modal.querySelector("#errorModal")
    );
    modalInstance.show();

    if (debugMode) {
      console.error("API请求失败:", error);
    }
  }
}

// 显示API文档
function showApiDocumentation() {
  const modal = document.createElement("div");
  modal.innerHTML = `
    <div class="modal fade" id="apiDocModal" tabindex="-1">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-book"></i> RAG 聊天 API 文档
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-12">
                <h6>API 端点</h6>
                <code class="d-block p-2 bg-light rounded mb-3">POST /api/v1/conversation/chat</code>

                <h6>请求参数</h6>
                <div class="table-responsive mb-3">
                  <table class="table table-sm table-bordered">
                    <thead>
                      <tr>
                        <th>参数名</th>
                        <th>类型</th>
                        <th>必填</th>
                        <th>说明</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><code>conversation_id</code></td>
                        <td>string</td>
                        <td>是</td>
                        <td>对话会话ID，用于区分不同的对话会话</td>
                      </tr>
                      <tr>
                        <td><code>question</code></td>
                        <td>string</td>
                        <td>是</td>
                        <td>用户问题</td>
                      </tr>
                      <tr>
                        <td><code>chat_engine_type</code></td>
                        <td>string</td>
                        <td>是</td>
                        <td>聊天引擎类型: "condense_plus_context" 或 "simple"</td>
                      </tr>
                      <tr>
                        <td><code>course_id</code></td>
                        <td>string</td>
                        <td>否</td>
                        <td>课程ID，用于过滤检索范围</td>
                      </tr>
                      <tr>
                        <td><code>course_material_id</code></td>
                        <td>string</td>
                        <td>否</td>
                        <td>课程材料ID，用于过滤检索范围</td>
                      </tr>
                      <tr>
                        <td><code>collection_name</code></td>
                        <td>string</td>
                        <td>否</td>
                        <td>集合名称，默认使用配置中的集合</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <h6>响应格式</h6>
                <pre class="bg-light p-3 rounded mb-3"><code>{
  "answer": "AI回答内容",
  "sources": [
    {
      "course_id": "课程ID",
      "course_material_id": "材料ID",
      "course_material_name": "材料名称",
      "chunk_text": "相关文本片段",
      "score": 0.95
    }
  ],
  "conversation_id": "对话ID",
  "chat_engine_type": "引擎类型",
  "filter_info": "过滤信息",
  "processing_time": 1.23
}</code></pre>

                <h6>使用示例</h6>
                <pre class="bg-light p-3 rounded"><code>curl -X POST "http://localhost:8000/api/v1/conversation/chat" \\
  -H "Content-Type: application/json" \\
  -d '{
    "conversation_id": "test_chat",
    "question": "什么是Python？",
    "chat_engine_type": "condense_plus_context",
    "course_id": "python_course"
  }'</code></pre>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <a href="/docs" target="_blank" class="btn btn-outline-primary">
              <i class="bi bi-box-arrow-up-right"></i> 完整API文档
            </a>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  const modalInstance = new bootstrap.Modal(
    modal.querySelector("#apiDocModal")
  );
  modalInstance.show();
}

// 复制参数到剪贴板
function copyPayloadToClipboard(payload) {
  navigator.clipboard
    .writeText(payload)
    .then(() => {
      showSuccess("请求参数已复制到剪贴板");
    })
    .catch(() => {
      showError("复制失败，请手动复制");
    });
}

// 复制响应到剪贴板
function copyResponseToClipboard(response) {
  navigator.clipboard
    .writeText(response)
    .then(() => {
      showSuccess("响应数据已复制到剪贴板");
    })
    .catch(() => {
      showError("复制失败，请手动复制");
    });
}
