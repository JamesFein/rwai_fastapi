// 扩展页面功能

// 刷新集合列表
function refreshCollections() {
  document.getElementById("collections-container").innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-3">正在刷新集合列表...</p>
        </div>
    `;
  loadCollections();
}

// 查看集合详情
async function viewCollectionInfo(collectionName) {
  try {
    const info = await RAGAPI.getCollectionInfo(collectionName);

    // 创建模态框显示详情
    const modalHTML = `
            <div class="modal fade" id="collectionInfoModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-info-circle"></i>
                                集合详情: ${collectionName}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>基本信息</h6>
                                    <table class="table table-sm">
                                        <tr><td>集合名称:</td><td>${
                                          info.name || collectionName
                                        }</td></tr>
                                        <tr><td>向量数量:</td><td>${
                                          info.vectors_count || 0
                                        }</td></tr>
                                        <tr><td>状态:</td><td><span class="badge bg-success">活跃</span></td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6>配置信息</h6>
                                    <pre class="bg-light p-2 rounded small">${JSON.stringify(
                                      info,
                                      null,
                                      2
                                    )}</pre>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

    // 移除已存在的模态框
    const existingModal = document.getElementById("collectionInfoModal");
    if (existingModal) {
      existingModal.remove();
    }

    // 添加新模态框
    document.body.insertAdjacentHTML("beforeend", modalHTML);

    // 显示模态框
    const modal = new bootstrap.Modal(
      document.getElementById("collectionInfoModal")
    );
    modal.show();
  } catch (error) {
    showError("获取集合详情失败: " + error.message);
  }
}

// 删除集合
async function deleteCollection(collectionName) {
  if (!confirm(`确定要删除集合 "${collectionName}" 吗？此操作不可撤销。`)) {
    return;
  }

  try {
    await RAGAPI.deleteCollection(collectionName);
    showSuccess("集合删除成功");
    refreshCollections();
  } catch (error) {
    showError("删除集合失败: " + error.message);
  }
}

// RAG 索引管理页面
function loadRagIndexPage(container) {
  container.innerHTML = `
        <div class="row">
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-database-add"></i>
                            建立文档索引
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="index-form">
                            <!-- 文件上传 -->
                            <div class="mb-4">
                                <label class="form-label">选择文档文件</label>
                                <div class="file-upload-area" id="index-file-drop-zone">
                                    <div class="file-upload-icon">
                                        <i class="bi bi-cloud-upload"></i>
                                    </div>
                                    <h6>拖拽文件到此处或点击选择</h6>
                                    <p class="text-muted mb-0">支持 .md 和 .txt 格式</p>
                                    <input type="file" id="index-file-input" class="d-none" accept=".md,.txt">
                                </div>
                                <div id="index-file-info" class="mt-2" style="display: none;">
                                    <div class="alert alert-info">
                                        <i class="bi bi-file-earmark-text"></i>
                                        <span id="index-file-name"></span>
                                        <span class="badge bg-secondary ms-2" id="index-file-size"></span>
                                    </div>
                                </div>
                            </div>

                            <!-- 元数据信息 -->
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="index-course-id" class="form-label">课程ID</label>
                                    <input type="text" class="form-control" id="index-course-id" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="index-course-material-id" class="form-label">课程材料ID</label>
                                    <input type="text" class="form-control" id="index-course-material-id" required>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="index-course-material-name" class="form-label">课程材料名称</label>
                                <input type="text" class="form-control" id="index-course-material-name" required>
                            </div>

                            <div class="mb-3">
                                <label for="index-collection-name" class="form-label">集合名称 (可选)</label>
                                <input type="text" class="form-control" id="index-collection-name" 
                                       placeholder="留空使用默认集合">
                            </div>

                            <button type="submit" class="btn btn-primary w-100">
                                <i class="bi bi-database-add"></i>
                                建立索引
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-info-circle"></i>
                            索引状态
                        </h5>
                    </div>
                    <div class="card-body">
                        <div id="index-result" class="text-center text-muted">
                            <i class="bi bi-database" style="font-size: 3rem; opacity: 0.3;"></i>
                            <p class="mt-3">请选择文件并建立索引</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 初始化文件上传
  initializeIndexFileUpload();

  // 绑定表单提交事件
  document
    .getElementById("index-form")
    .addEventListener("submit", handleIndexFormSubmit);
}

// 初始化索引页面的文件上传
function initializeIndexFileUpload() {
  const dropZone = document.getElementById("index-file-drop-zone");
  const fileInput = document.getElementById("index-file-input");
  const fileInfo = document.getElementById("index-file-info");
  const fileName = document.getElementById("index-file-name");
  const fileSize = document.getElementById("index-file-size");

  // 创建拖拽上传实例并存储到全局变量
  window.indexFileUploader = new DragDropUploader(dropZone, fileInput, {
    onSuccess: (file) => {
      fileName.textContent = file.name;
      fileSize.textContent = formatFileSize(file.size);
      fileInfo.style.display = "block";

      // 自动填充材料名称
      const materialNameInput = document.getElementById(
        "index-course-material-name"
      );
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

// 处理索引表单提交
async function handleIndexFormSubmit(e) {
  e.preventDefault();

  // 使用上传器获取选中的文件
  const file = window.indexFileUploader
    ? window.indexFileUploader.getSelectedFile()
    : null;

  if (!file) {
    showError("请先选择要索引的文件");
    return;
  }

  // 收集表单数据
  const formData = new FormData();
  formData.append("file", file);
  formData.append(
    "course_id",
    document.getElementById("index-course-id").value
  );
  formData.append(
    "course_material_id",
    document.getElementById("index-course-material-id").value
  );
  formData.append(
    "course_material_name",
    document.getElementById("index-course-material-name").value
  );

  const collectionName = document.getElementById("index-collection-name").value;
  if (collectionName) {
    formData.append("collection_name", collectionName);
  }

  try {
    showLoading();

    // 调用API建立索引
    const response = await RAGAPI.buildIndex(formData);

    hideLoading();

    // 显示结果
    displayIndexResult(response);

    showSuccess("索引建立成功！");
  } catch (error) {
    hideLoading();
    showError("建立索引失败: " + error.message);
  }
}

// 显示索引结果
function displayIndexResult(result) {
  const resultContainer = document.getElementById("index-result");

  resultContainer.innerHTML = `
        <div class="text-start">
            <div class="alert alert-success">
                <i class="bi bi-check-circle"></i>
                索引建立成功！
            </div>
            
            <div class="row">
                <div class="col-6">
                    <div class="text-center">
                        <h4 class="text-primary">${result.document_count}</h4>
                        <p class="text-muted mb-0">文档数量</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h4 class="text-success">${result.chunk_count}</h4>
                        <p class="text-muted mb-0">文本块数量</p>
                    </div>
                </div>
            </div>
            
            <div class="mt-3">
                <p class="mb-1"><strong>处理结果:</strong></p>
                <p class="text-muted">${result.message}</p>
            </div>
        </div>
    `;
}

// 统一处理页面
function loadUnifiedProcessPage(container) {
  container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-gear"></i>
                    统一课程材料处理
                </h5>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    <strong>一站式处理:</strong> 上传文件后将自动完成大纲生成和RAG索引建立
                </div>
                
                <form id="unified-process-form">
                    <!-- 文件上传区域 -->
                    <div class="mb-4">
                        <label class="form-label">选择课程材料文件</label>
                        <div class="file-upload-area" id="unified-file-drop-zone">
                            <div class="file-upload-icon">
                                <i class="bi bi-cloud-upload"></i>
                            </div>
                            <h6>拖拽文件到此处或点击选择</h6>
                            <p class="text-muted mb-0">支持 .md 和 .txt 格式，最大 10MB</p>
                            <input type="file" id="unified-file-input" class="d-none" accept=".md,.txt">
                        </div>
                        <div id="unified-file-info" class="mt-2" style="display: none;">
                            <div class="alert alert-info">
                                <i class="bi bi-file-earmark-text"></i>
                                <span id="unified-file-name"></span>
                                <span class="badge bg-secondary ms-2" id="unified-file-size"></span>
                            </div>
                        </div>
                    </div>

                    <!-- 基本信息 -->
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="unified-course-id" class="form-label">课程ID</label>
                            <input type="text" class="form-control" id="unified-course-id" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="unified-course-material-id" class="form-label">课程材料ID</label>
                            <input type="text" class="form-control" id="unified-course-material-id" required>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="unified-material-name" class="form-label">材料名称</label>
                        <input type="text" class="form-control" id="unified-material-name" required>
                    </div>

                    <!-- 处理选项 -->
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">大纲生成选项</h6>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label for="unified-custom-prompt" class="form-label">自定义提示词</label>
                                        <textarea class="form-control" id="unified-custom-prompt" rows="2"></textarea>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="unified-include-refine" checked>
                                        <label class="form-check-label" for="unified-include-refine">
                                            启用大纲精简
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">RAG索引选项</h6>
                                </div>
                                <div class="card-body">
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="checkbox" id="unified-enable-rag" checked>
                                        <label class="form-check-label" for="unified-enable-rag">
                                            启用RAG索引建立
                                        </label>
                                    </div>
                                    <div class="mb-3">
                                        <label for="unified-rag-collection" class="form-label">RAG集合名称</label>
                                        <input type="text" class="form-control" id="unified-rag-collection" 
                                               placeholder="留空使用默认集合">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg w-100 mt-3">
                        <i class="bi bi-gear"></i>
                        开始统一处理
                    </button>
                </form>

                <!-- 处理进度 -->
                <div id="unified-progress" class="mt-4" style="display: none;">
                    <h6>处理进度</h6>
                    <div class="progress mb-3">
                        <div class="progress-bar" id="unified-progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                    <div id="unified-status-text">准备开始...</div>
                </div>

                <!-- 处理结果 -->
                <div id="unified-results" class="mt-4" style="display: none;">
                    <!-- 结果将在这里显示 -->
                </div>
            </div>
        </div>
    `;

  // 初始化文件上传
  initializeUnifiedFileUpload();

  // 绑定表单提交事件
  document
    .getElementById("unified-process-form")
    .addEventListener("submit", handleUnifiedProcessSubmit);
}

// 初始化统一处理页面的文件上传
function initializeUnifiedFileUpload() {
  const dropZone = document.getElementById("unified-file-drop-zone");
  const fileInput = document.getElementById("unified-file-input");
  const fileInfo = document.getElementById("unified-file-info");
  const fileName = document.getElementById("unified-file-name");
  const fileSize = document.getElementById("unified-file-size");

  // 创建拖拽上传实例并存储到全局变量
  window.unifiedFileUploader = new DragDropUploader(dropZone, fileInput, {
    onSuccess: (file) => {
      fileName.textContent = file.name;
      fileSize.textContent = formatFileSize(file.size);
      fileInfo.style.display = "block";

      // 自动填充材料名称
      const materialNameInput = document.getElementById(
        "unified-material-name"
      );
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

// 处理统一处理表单提交
async function handleUnifiedProcessSubmit(e) {
  e.preventDefault();

  // 使用上传器获取选中的文件
  const file = window.unifiedFileUploader
    ? window.unifiedFileUploader.getSelectedFile()
    : null;

  if (!file) {
    showError("请先选择要处理的文件");
    return;
  }

  // 收集表单数据
  const formData = new FormData();
  formData.append("file", file);
  formData.append(
    "course_id",
    document.getElementById("unified-course-id").value
  );
  formData.append(
    "course_material_id",
    document.getElementById("unified-course-material-id").value
  );
  formData.append(
    "material_name",
    document.getElementById("unified-material-name").value
  );
  formData.append(
    "include_refine",
    document.getElementById("unified-include-refine").checked
  );
  formData.append(
    "enable_rag_indexing",
    document.getElementById("unified-enable-rag").checked
  );

  const customPrompt = document.getElementById("unified-custom-prompt").value;
  if (customPrompt) {
    formData.append("custom_prompt", customPrompt);
  }

  const ragCollection = document.getElementById("unified-rag-collection").value;
  if (ragCollection) {
    formData.append("rag_collection_name", ragCollection);
  }

  try {
    // 显示进度条
    showUnifiedProgress();

    // 调用API统一处理
    const response = await CourseMaterialAPI.processCourseMaterial(formData);

    // 开始轮询任务状态
    startUnifiedTaskPolling(response.task_id);
  } catch (error) {
    hideUnifiedProgress();
    showError("统一处理失败: " + error.message);
  }
}

// 显示统一处理进度
function showUnifiedProgress() {
  const progressDiv = document.getElementById("unified-progress");
  const progressBar = document.getElementById("unified-progress-bar");
  const statusText = document.getElementById("unified-status-text");

  progressDiv.style.display = "block";
  progressBar.style.width = "10%";
  statusText.textContent = "正在启动处理流程...";
}

// 隐藏统一处理进度
function hideUnifiedProgress() {
  const progressDiv = document.getElementById("unified-progress");
  progressDiv.style.display = "none";
}

// 开始统一任务轮询
function startUnifiedTaskPolling(taskId) {
  const poller = new TaskPoller(
    CourseMaterialAPI.getTaskStatus,
    taskId,
    updateUnifiedTaskStatus,
    handleUnifiedTaskComplete,
    handleUnifiedTaskError
  );

  poller.start(2000); // 每2秒轮询一次
}

// 更新统一任务状态
function updateUnifiedTaskStatus(taskData) {
  const progressBar = document.getElementById("unified-progress-bar");
  const statusText = document.getElementById("unified-status-text");

  if (progressBar && statusText) {
    progressBar.style.width = taskData.progress_percentage + "%";
    statusText.textContent = `${taskData.current_step} (${taskData.completed_steps}/${taskData.total_steps})`;
  }
}

// 处理统一任务完成
function handleUnifiedTaskComplete(taskData) {
  hideUnifiedProgress();

  if (taskData.status === "completed") {
    showSuccess("课程材料处理完成！");
    displayUnifiedResults(taskData);
  } else if (taskData.status === "failed") {
    showError("课程材料处理失败: " + (taskData.error_message || "未知错误"));
  }
}

// 处理统一任务错误
function handleUnifiedTaskError(error) {
  hideUnifiedProgress();
  showError("任务状态查询失败: " + error.message);
}

// 显示统一处理结果
function displayUnifiedResults(taskData) {
  const resultsDiv = document.getElementById("unified-results");

  resultsDiv.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">
                    <i class="bi bi-check-circle text-success"></i>
                    处理完成
                </h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>大纲生成结果</h6>
                        ${
                          taskData.outline_content
                            ? `
                            <div class="border rounded p-3 mb-3" style="max-height: 200px; overflow-y: auto;">
                                ${marked.parse(taskData.outline_content)}
                            </div>
                            <button class="btn btn-sm btn-outline-primary" onclick="downloadOutline('${
                              taskData.original_filename
                            }', \`${taskData.outline_content.replace(
                                /`/g,
                                "\\`"
                              )}\`)">
                                <i class="bi bi-download"></i> 下载大纲
                            </button>
                        `
                            : '<p class="text-muted">大纲生成未完成</p>'
                        }
                    </div>
                    <div class="col-md-6">
                        <h6>RAG索引结果</h6>
                        ${
                          taskData.rag_index_status === "completed"
                            ? `
                            <div class="alert alert-success">
                                <i class="bi bi-check-circle"></i>
                                索引建立成功
                            </div>
                            <p><strong>集合名称:</strong> ${taskData.rag_collection_name}</p>
                            <p><strong>文档数量:</strong> ${taskData.rag_document_count}</p>
                        `
                            : '<p class="text-muted">RAG索引未启用或未完成</p>'
                        }
                    </div>
                </div>

                <div class="mt-3">
                    <h6>处理信息</h6>
                    <div class="row">
                        <div class="col-md-4">
                            <small class="text-muted">总处理时间:</small><br>
                            <strong>${formatTime(
                              taskData.total_processing_time || 0
                            )}</strong>
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted">文件大小:</small><br>
                            <strong>${formatFileSize(
                              taskData.file_size || 0
                            )}</strong>
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted">完成时间:</small><br>
                            <strong>${formatDateTime(
                              taskData.completed_at || new Date()
                            )}</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  resultsDiv.style.display = "block";
}

// 健康状态页面
function loadHealthStatusPage(container) {
  container.innerHTML = `
        <div class="row">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="bi bi-heart-pulse"></i>
                            系统健康状态
                        </h5>
                        <button class="btn btn-outline-primary btn-sm" onclick="refreshHealthStatus()">
                            <i class="bi bi-arrow-clockwise"></i> 刷新
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="health-status-container">
                            <div class="text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">加载中...</span>
                                </div>
                                <p class="mt-3">正在检查系统状态...</p>
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
                            快速检查
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="checkMainAPI()">
                                <i class="bi bi-server"></i> 检查主API
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="checkOutlineAPI()">
                                <i class="bi bi-file-text"></i> 检查大纲API
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="checkRAGAPI()">
                                <i class="bi bi-chat-dots"></i> 检查RAG API
                            </button>
                            <button class="btn btn-outline-warning btn-sm" onclick="checkCourseMaterialAPI()">
                                <i class="bi bi-gear"></i> 检查课程材料API
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 加载健康状态
  loadHealthStatus();
}

// 加载健康状态
async function loadHealthStatus() {
  try {
    const [mainHealth, courseMaterialHealth] = await Promise.allSettled([
      SystemAPI.getHealth(),
      CourseMaterialAPI.getHealth(),
    ]);

    displayHealthStatus({
      main: mainHealth,
      courseMaterial: courseMaterialHealth,
    });
  } catch (error) {
    document.getElementById("health-status-container").innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                加载健康状态失败: ${error.message}
            </div>
        `;
  }
}

// 显示健康状态
function displayHealthStatus(healthData) {
  const container = document.getElementById("health-status-container");

  container.innerHTML = `
        <div class="row">
            <div class="col-md-6 mb-3">
                <div class="card ${
                  healthData.main.status === "fulfilled"
                    ? "border-success"
                    : "border-danger"
                }">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="bi bi-server"></i>
                            主系统API
                        </h6>
                        ${
                          healthData.main.status === "fulfilled"
                            ? `
                            <span class="badge bg-success">在线</span>
                            <div class="mt-2 small">
                                <div>版本: ${
                                  healthData.main.value.version
                                }</div>
                                <div>运行时间: ${formatTime(
                                  healthData.main.value.uptime
                                )}</div>
                                <div>OpenAI状态: ${
                                  healthData.main.value.openai_api
                                }</div>
                            </div>
                        `
                            : `
                            <span class="badge bg-danger">离线</span>
                            <div class="mt-2 small text-danger">
                                ${healthData.main.reason.message}
                            </div>
                        `
                        }
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="card ${
                  healthData.courseMaterial.status === "fulfilled"
                    ? "border-success"
                    : "border-danger"
                }">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="bi bi-gear"></i>
                            课程材料API
                        </h6>
                        ${
                          healthData.courseMaterial.status === "fulfilled"
                            ? `
                            <span class="badge bg-success">在线</span>
                            <div class="mt-2 small">
                                服务正常运行
                            </div>
                        `
                            : `
                            <span class="badge bg-danger">离线</span>
                            <div class="mt-2 small text-danger">
                                ${healthData.courseMaterial.reason.message}
                            </div>
                        `
                        }
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-3">
            <h6>系统概览</h6>
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-${
                          AppState.systemStatus === "online"
                            ? "success"
                            : "danger"
                        }">${
    AppState.systemStatus === "online" ? "在线" : "离线"
  }</h4>
                        <p class="text-muted mb-0">总体状态</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-info">${new Date().toLocaleTimeString(
                          "zh-CN"
                        )}</h4>
                        <p class="text-muted mb-0">当前时间</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-primary">${AppState.theme}</h4>
                        <p class="text-muted mb-0">当前主题</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4 class="text-warning">${AppState.currentPage}</h4>
                        <p class="text-muted mb-0">当前页面</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 刷新健康状态
function refreshHealthStatus() {
  document.getElementById("health-status-container").innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-3">正在刷新健康状态...</p>
        </div>
    `;
  loadHealthStatus();
}

// 快速检查函数
async function checkMainAPI() {
  try {
    const result = await SystemAPI.getHealth();
    showSuccess("主API检查通过");
  } catch (error) {
    showError("主API检查失败: " + error.message);
  }
}

async function checkOutlineAPI() {
  try {
    const result = await OutlineAPI.getMetrics();
    showSuccess("大纲API检查通过");
  } catch (error) {
    showError("大纲API检查失败: " + error.message);
  }
}

async function checkRAGAPI() {
  try {
    const result = await RAGAPI.getCollections();
    showSuccess("RAG API检查通过");
  } catch (error) {
    showError("RAG API检查失败: " + error.message);
  }
}

async function checkCourseMaterialAPI() {
  try {
    const result = await CourseMaterialAPI.getHealth();
    showSuccess("课程材料API检查通过");
  } catch (error) {
    showError("课程材料API检查失败: " + error.message);
  }
}

// 材料管理页面
function loadMaterialManagementPage(container) {
  container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-folder"></i>
                    材料管理
                </h5>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    <strong>提示:</strong> 此页面用于管理已上传的课程材料，包括查看、下载和删除操作。
                </div>

                <div class="row mb-3">
                    <div class="col-md-6">
                        <input type="text" class="form-control" id="search-course-id"
                               placeholder="按课程ID搜索...">
                    </div>
                    <div class="col-md-6">
                        <button class="btn btn-primary" onclick="searchMaterials()">
                            <i class="bi bi-search"></i> 搜索
                        </button>
                        <button class="btn btn-outline-secondary ms-2" onclick="loadAllMaterials()">
                            <i class="bi bi-list"></i> 显示全部
                        </button>
                    </div>
                </div>

                <div id="materials-container">
                    <div class="text-center text-muted">
                        <i class="bi bi-folder-x" style="font-size: 3rem; opacity: 0.3;"></i>
                        <p class="mt-3">请使用搜索功能查找材料</p>
                        <p class="small">或点击"显示全部"查看所有材料</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 搜索材料
function searchMaterials() {
  const courseId = document.getElementById("search-course-id").value.trim();
  if (!courseId) {
    showError("请输入课程ID");
    return;
  }

  // 这里应该调用API搜索材料，但由于当前API不支持，我们显示一个示例
  const container = document.getElementById("materials-container");
  container.innerHTML = `
        <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle"></i>
            材料搜索功能正在开发中，请使用其他页面管理材料。
        </div>
    `;
}

// 加载所有材料
function loadAllMaterials() {
  const container = document.getElementById("materials-container");
  container.innerHTML = `
        <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle"></i>
            材料列表功能正在开发中，请使用任务管理页面查看处理历史。
        </div>
    `;
}

// 清理工具页面
function loadCleanupToolsPage(container) {
  container.innerHTML = `
        <div class="row">
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-trash"></i>
                            清理指定材料
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="cleanup-material-form">
                            <div class="mb-3">
                                <label for="cleanup-course-id" class="form-label">课程ID</label>
                                <input type="text" class="form-control" id="cleanup-course-id" required>
                            </div>

                            <div class="mb-3">
                                <label for="cleanup-material-id" class="form-label">课程材料ID</label>
                                <input type="text" class="form-control" id="cleanup-material-id" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">清理选项</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="cleanup-files" checked>
                                    <label class="form-check-label" for="cleanup-files">
                                        清理文件
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="cleanup-rag-data" checked>
                                    <label class="form-check-label" for="cleanup-rag-data">
                                        清理RAG数据
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="cleanup-task-data" checked>
                                    <label class="form-check-label" for="cleanup-task-data">
                                        清理任务数据
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="force-cleanup">
                                    <label class="form-check-label" for="force-cleanup">
                                        强制清理
                                    </label>
                                </div>
                            </div>

                            <button type="submit" class="btn btn-danger w-100">
                                <i class="bi bi-trash"></i>
                                清理材料
                            </button>
                        </form>

                        <!-- RAG v2 清理选项 -->
                        <div class="mt-3">
                            <h6 class="text-muted">RAG v2 清理选项</h6>
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-warning btn-sm" onclick="cleanupRAGDocumentsByMaterial()">
                                    <i class="bi bi-database-dash"></i>
                                    仅清理RAG文档 (v2)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-trash-fill"></i>
                            清理整个课程
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle"></i>
                            <strong>警告:</strong> 此操作将删除指定课程的所有材料和数据，不可撤销！
                        </div>

                        <form id="cleanup-course-form">
                            <div class="mb-3">
                                <label for="cleanup-course-id-full" class="form-label">课程ID</label>
                                <input type="text" class="form-control" id="cleanup-course-id-full" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">清理选项</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="cleanup-course-files" checked>
                                    <label class="form-check-label" for="cleanup-course-files">
                                        清理所有文件
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="cleanup-course-rag-data" checked>
                                    <label class="form-check-label" for="cleanup-course-rag-data">
                                        清理所有RAG数据
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="cleanup-course-task-data" checked>
                                    <label class="form-check-label" for="cleanup-course-task-data">
                                        清理所有任务数据
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="force-cleanup-course">
                                    <label class="form-check-label" for="force-cleanup-course">
                                        强制清理
                                    </label>
                                </div>
                            </div>

                            <button type="submit" class="btn btn-danger w-100">
                                <i class="bi bi-trash-fill"></i>
                                清理整个课程
                            </button>
                        </form>

                        <!-- RAG v2 清理选项 -->
                        <div class="mt-3">
                            <h6 class="text-muted">RAG v2 清理选项</h6>
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-warning btn-sm" onclick="cleanupRAGDocumentsByCourse()">
                                    <i class="bi bi-database-dash"></i>
                                    仅清理RAG文档 (v2)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 清理结果 -->
        <div id="cleanup-results" class="mt-4" style="display: none;">
            <!-- 清理结果将在这里显示 -->
        </div>
    `;

  // 绑定表单提交事件
  document
    .getElementById("cleanup-material-form")
    .addEventListener("submit", handleCleanupMaterial);
  document
    .getElementById("cleanup-course-form")
    .addEventListener("submit", handleCleanupCourse);
}

// 处理清理材料
async function handleCleanupMaterial(e) {
  e.preventDefault();

  const courseId = document.getElementById("cleanup-course-id").value;
  const materialId = document.getElementById("cleanup-material-id").value;

  if (
    !confirm(
      `确定要清理课程 "${courseId}" 中的材料 "${materialId}" 吗？此操作不可撤销。`
    )
  ) {
    return;
  }

  const options = {
    cleanup_files: document.getElementById("cleanup-files").checked,
    cleanup_rag_data: document.getElementById("cleanup-rag-data").checked,
    cleanup_task_data: document.getElementById("cleanup-task-data").checked,
    force_cleanup: document.getElementById("force-cleanup").checked,
  };

  try {
    showLoading();

    const response = await CourseMaterialAPI.cleanupMaterial(
      courseId,
      materialId,
      options
    );

    hideLoading();
    showSuccess("材料清理完成");
    displayCleanupResults(response);
  } catch (error) {
    hideLoading();
    showError("清理材料失败: " + error.message);
  }
}

// 处理清理课程
async function handleCleanupCourse(e) {
  e.preventDefault();

  const courseId = document.getElementById("cleanup-course-id-full").value;

  if (
    !confirm(
      `确定要清理整个课程 "${courseId}" 吗？这将删除该课程的所有材料和数据，此操作不可撤销。`
    )
  ) {
    return;
  }

  const options = {
    cleanup_files: document.getElementById("cleanup-course-files").checked,
    cleanup_rag_data: document.getElementById("cleanup-course-rag-data")
      .checked,
    cleanup_task_data: document.getElementById("cleanup-course-task-data")
      .checked,
    force_cleanup: document.getElementById("force-cleanup-course").checked,
  };

  try {
    showLoading();

    const response = await CourseMaterialAPI.cleanupCourse(courseId, options);

    hideLoading();
    showSuccess("课程清理完成");
    displayCleanupResults(response);
  } catch (error) {
    hideLoading();
    showError("清理课程失败: " + error.message);
  }
}

// 显示清理结果
function displayCleanupResults(result) {
  const resultsDiv = document.getElementById("cleanup-results");

  resultsDiv.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">
                    <i class="bi bi-check-circle text-success"></i>
                    清理完成
                </h6>
            </div>
            <div class="card-body">
                <div class="alert alert-success">
                    <i class="bi bi-check-circle"></i>
                    ${result.message || "清理操作已完成"}
                </div>

                ${
                  result.details
                    ? `
                    <h6>清理详情</h6>
                    <div class="row">
                        ${
                          result.details.files_cleaned
                            ? `
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-primary">${result.details.files_cleaned}</h4>
                                    <p class="text-muted mb-0">文件已清理</p>
                                </div>
                            </div>
                        `
                            : ""
                        }
                        ${
                          result.details.rag_data_cleaned
                            ? `
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-success">${result.details.rag_data_cleaned}</h4>
                                    <p class="text-muted mb-0">RAG数据已清理</p>
                                </div>
                            </div>
                        `
                            : ""
                        }
                        ${
                          result.details.tasks_cleaned
                            ? `
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-info">${result.details.tasks_cleaned}</h4>
                                    <p class="text-muted mb-0">任务已清理</p>
                                </div>
                            </div>
                        `
                            : ""
                        }
                        ${
                          result.details.total_size_freed
                            ? `
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-warning">${formatFileSize(
                                      result.details.total_size_freed
                                    )}</h4>
                                    <p class="text-muted mb-0">空间已释放</p>
                                </div>
                            </div>
                        `
                            : ""
                        }
                    </div>
                `
                    : ""
                }

                <div class="mt-3">
                    <small class="text-muted">
                        清理时间: ${formatDateTime(new Date())}
                    </small>
                </div>
            </div>
        </div>
    `;

  resultsDiv.style.display = "block";
}

// RAG v2 清理函数
async function cleanupRAGDocumentsByMaterial() {
  const courseId = document.getElementById("cleanup-course-id").value;
  const materialId = document.getElementById("cleanup-material-id").value;

  if (!courseId || !materialId) {
    showError("请填写课程ID和材料ID");
    return;
  }

  if (
    !confirm(
      `确定要清理课程 "${courseId}" 中材料 "${materialId}" 的RAG文档吗？`
    )
  ) {
    return;
  }

  try {
    showLoading();
    const response = await RAGAPI.deleteDocumentsByMaterial(
      courseId,
      materialId
    );
    hideLoading();

    showSuccess(`RAG文档清理完成，删除了 ${response.deleted_count} 个文档`);
    displayCleanupResults({
      message: `RAG文档清理完成`,
      deleted_count: response.deleted_count,
      course_id: courseId,
      material_id: materialId,
    });
  } catch (error) {
    hideLoading();
    showError("RAG文档清理失败: " + error.message);
  }
}

async function cleanupRAGDocumentsByCourse() {
  const courseId = document.getElementById("cleanup-course-id-full").value;

  if (!courseId) {
    showError("请填写课程ID");
    return;
  }

  if (
    !confirm(`确定要清理课程 "${courseId}" 的所有RAG文档吗？此操作不可撤销！`)
  ) {
    return;
  }

  try {
    showLoading();
    const response = await RAGAPI.deleteDocumentsByCourse(courseId);
    hideLoading();

    showSuccess(`RAG文档清理完成，删除了 ${response.deleted_count} 个文档`);
    displayCleanupResults({
      message: `RAG文档清理完成`,
      deleted_count: response.deleted_count,
      course_id: courseId,
    });
  } catch (error) {
    hideLoading();
    showError("RAG文档清理失败: " + error.message);
  }
}
