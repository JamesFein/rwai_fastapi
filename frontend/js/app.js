// 全局应用状态
const AppState = {
  currentPage: "outline-generate",
  theme: localStorage.getItem("theme") || "light",
  apiBaseUrl: "http://localhost:8000", // 指向独立的FastAPI后端服务
  systemStatus: "unknown",
};

// 应用初始化
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

// 初始化应用
function initializeApp() {
  // 设置主题
  setTheme(AppState.theme);

  // 检查系统状态
  checkSystemHealth();

  // 加载默认页面
  showPage("outline-generate");

  // 设置定时器检查系统状态
  setInterval(checkSystemHealth, 30000); // 每30秒检查一次

  console.log("AI Backend API 控制台已初始化");
}

// 页面切换功能
function showPage(pageId) {
  // 隐藏所有页面
  const allPages = document.querySelectorAll(".page-content");
  allPages.forEach((page) => page.classList.remove("active"));

  // 移除所有导航链接的active状态
  const allNavLinks = document.querySelectorAll(".sidebar .nav-link");
  allNavLinks.forEach((link) => link.classList.remove("active"));

  // 显示目标页面
  const targetPage = document.getElementById(pageId + "-page");
  if (targetPage) {
    targetPage.classList.add("active");
    targetPage.classList.add("fade-in");
  } else {
    // 如果页面不存在，动态创建
    createPage(pageId);
  }

  // 设置对应导航链接为active
  const targetNavLink = document.querySelector(
    `[onclick="showPage('${pageId}')"]`
  );
  if (targetNavLink) {
    targetNavLink.classList.add("active");
  }

  // 更新页面标题
  updatePageTitle(pageId);

  // 更新应用状态
  AppState.currentPage = pageId;

  // 加载页面内容
  loadPageContent(pageId);
}

// 更新页面标题
function updatePageTitle(pageId) {
  const titles = {
    "outline-generate": "大纲生成",
    "task-management": "任务管理",
    "performance-monitor": "性能监控",
    "rag-chat": "智能问答",
    "rag-index": "索引管理",
    "collection-management": "集合管理",
    "unified-process": "统一处理",
    "material-management": "材料管理",
    "cleanup-tools": "清理工具",
    "health-status": "健康状态",
  };

  const title = titles[pageId] || "未知页面";
  document.getElementById("page-title").textContent = title;
}

// 动态创建页面
function createPage(pageId) {
  const pageContent = document.getElementById("page-content");
  const newPage = document.createElement("div");
  newPage.id = pageId + "-page";
  newPage.className = "page-content active fade-in";

  // 根据页面ID设置初始内容
  newPage.innerHTML = `
        <div class="d-flex justify-content-center align-items-center" style="height: 300px;">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-3">正在加载页面内容...</p>
            </div>
        </div>
    `;

  pageContent.appendChild(newPage);
}

// 加载页面内容
function loadPageContent(pageId) {
  const page = document.getElementById(pageId + "-page");
  if (!page) return;

  // 根据页面ID加载对应内容
  switch (pageId) {
    case "outline-generate":
      loadOutlineGeneratePage(page);
      break;
    case "task-management":
      loadTaskManagementPage(page);
      break;
    case "performance-monitor":
      loadPerformanceMonitorPage(page);
      break;
    case "rag-chat":
      loadRagChatPage(page);
      break;
    case "rag-index":
      loadRagIndexPage(page);
      break;
    case "collection-management":
      loadCollectionManagementPage(page);
      break;
    case "unified-process":
      loadUnifiedProcessPage(page);
      break;
    case "material-management":
      loadMaterialManagementPage(page);
      break;
    case "cleanup-tools":
      loadCleanupToolsPage(page);
      break;
    case "health-status":
      loadHealthStatusPage(page);
      break;
    default:
      page.innerHTML =
        '<div class="alert alert-warning">页面内容正在开发中...</div>';
  }
}

// 检查系统健康状态
async function checkSystemHealth() {
  try {
    const response = await fetch(`${AppState.apiBaseUrl}/health`);
    const data = await response.json();

    if (response.ok) {
      AppState.systemStatus = "online";
      updateSystemStatusIndicator("online", "在线");
    } else {
      AppState.systemStatus = "error";
      updateSystemStatusIndicator("error", "错误");
    }
  } catch (error) {
    AppState.systemStatus = "offline";
    updateSystemStatusIndicator("offline", "离线");
    console.error("系统健康检查失败:", error);
  }
}

// 更新系统状态指示器
function updateSystemStatusIndicator(status, text) {
  const statusElement = document.getElementById("system-status");
  if (!statusElement) return;

  // 移除所有状态类
  statusElement.className = "badge";

  // 根据状态设置样式
  switch (status) {
    case "online":
      statusElement.classList.add("bg-success");
      statusElement.innerHTML = '<i class="bi bi-circle-fill"></i> ' + text;
      break;
    case "offline":
      statusElement.classList.add("bg-danger");
      statusElement.innerHTML = '<i class="bi bi-circle-fill"></i> ' + text;
      break;
    case "error":
      statusElement.classList.add("bg-warning");
      statusElement.innerHTML =
        '<i class="bi bi-exclamation-circle-fill"></i> ' + text;
      break;
    default:
      statusElement.classList.add("bg-secondary");
      statusElement.innerHTML =
        '<i class="bi bi-question-circle-fill"></i> 未知';
  }
}

// 刷新状态
function refreshStatus() {
  checkSystemHealth();

  // 重新加载当前页面内容
  loadPageContent(AppState.currentPage);

  // 显示刷新动画
  const refreshBtn = document.querySelector('[onclick="refreshStatus()"]');
  if (refreshBtn) {
    const icon = refreshBtn.querySelector("i");
    icon.classList.add("pulse");
    setTimeout(() => icon.classList.remove("pulse"), 1000);
  }
}

// 主题切换
function toggleTheme() {
  const newTheme = AppState.theme === "light" ? "dark" : "light";
  setTheme(newTheme);
}

// 设置主题
function setTheme(theme) {
  AppState.theme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);

  // 更新主题切换按钮图标
  const themeBtn = document.querySelector('[onclick="toggleTheme()"]');
  if (themeBtn) {
    const icon = themeBtn.querySelector("i");
    icon.className = theme === "light" ? "bi bi-moon" : "bi bi-sun";
  }
}

// 显示加载状态
function showLoading() {
  const loadingModal = new bootstrap.Modal(
    document.getElementById("loadingModal")
  );
  loadingModal.show();
}

// 隐藏加载状态
function hideLoading() {
  try {
    const loadingModal = bootstrap.Modal.getInstance(
      document.getElementById("loadingModal")
    );
    if (loadingModal) {
      loadingModal.hide();
    }
  } catch (error) {
    console.error("隐藏加载动画失败:", error);
    // 强制隐藏模态框
    const modalElement = document.getElementById("loadingModal");
    if (modalElement) {
      modalElement.style.display = "none";
      modalElement.classList.remove("show");
      document.body.classList.remove("modal-open");
      // 移除backdrop
      const backdrop = document.querySelector(".modal-backdrop");
      if (backdrop) {
        backdrop.remove();
      }
    }
  }
}

// 显示错误信息
function showError(message) {
  document.getElementById("error-message").textContent = message;
  const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
  errorModal.show();
}

// 显示成功提示
function showSuccess(message) {
  // 创建成功提示元素
  const alertDiv = document.createElement("div");
  alertDiv.className =
    "alert alert-success alert-dismissible fade show position-fixed";
  alertDiv.style.cssText =
    "top: 80px; right: 20px; z-index: 9999; min-width: 300px;";
  alertDiv.innerHTML = `
        <i class="bi bi-check-circle-fill"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(alertDiv);

  // 3秒后自动移除
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.parentNode.removeChild(alertDiv);
    }
  }, 3000);
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// 格式化时间
function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}秒`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}分${remainingSeconds}秒`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}小时${minutes}分钟`;
  }
}

// 格式化日期时间
function formatDateTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// 复制到剪贴板
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showSuccess("已复制到剪贴板");
  } catch (err) {
    console.error("复制失败:", err);
    showError("复制失败");
  }
}

// 下载文件
function downloadFile(content, filename, contentType = "text/plain") {
  const blob = new Blob([content], { type: contentType });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
