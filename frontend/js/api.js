// API 调用模块
class APIClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  // 通用请求方法
  async request(url, options = {}) {
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(this.baseUrl + url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error("API请求失败:", error);
      throw error;
    }
  }

  // GET 请求
  async get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request(fullUrl, { method: "GET" });
  }

  // POST 请求
  async post(url, data = {}) {
    return this.request(url, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // POST 表单数据
  async postForm(url, formData) {
    return this.request(url, {
      method: "POST",
      headers: {}, // 不设置Content-Type，让浏览器自动设置
      body: formData,
    });
  }

  // DELETE 请求
  async delete(url) {
    return this.request(url, { method: "DELETE" });
  }

  // PUT 请求
  async put(url, data = {}) {
    return this.request(url, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }
}

// 创建API客户端实例
const api = new APIClient(AppState.apiBaseUrl);

// 系统API
const SystemAPI = {
  // 获取系统健康状态
  async getHealth() {
    return api.get("/health");
  },

  // 获取根信息
  async getRoot() {
    return api.get("/");
  },
};

// 大纲生成API
const OutlineAPI = {
  // 生成大纲
  async generateOutline(formData) {
    return api.postForm("/api/v1/outline/generate", formData);
  },

  // 查询任务状态
  async getTaskStatus(taskId) {
    return api.get(`/api/v1/outline/task/${taskId}`);
  },

  // 获取任务列表
  async getTasks() {
    return api.get("/api/v1/outline/tasks");
  },

  // 删除任务
  async deleteTask(taskId) {
    return api.delete(`/api/v1/outline/task/${taskId}`);
  },

  // 获取性能指标
  async getMetrics() {
    return api.get("/api/v1/outline/metrics");
  },

  // 获取大纲文件
  async getOutlineFile(courseId, courseMaterialId) {
    return api.get(`/api/v1/outline/file/${courseId}/${courseMaterialId}`);
  },
};

// RAG API
const RAGAPI = {
  // 建立索引
  async buildIndex(formData) {
    return api.postForm("/api/v1/rag/index", formData);
  },

  // RAG查询
  async query(queryData) {
    return api.post("/api/v1/rag/query", queryData);
  },

  // 获取集合列表
  async getCollections() {
    return api.get("/api/v1/rag/collections");
  },

  // 删除集合
  async deleteCollection(collectionName) {
    return api.delete(`/api/v1/rag/collections/${collectionName}`);
  },

  // 获取集合信息
  async getCollectionInfo(collectionName) {
    return api.get(`/api/v1/rag/collections/${collectionName}/info`);
  },
};

// 课程材料API
const CourseMaterialAPI = {
  // 统一处理课程材料
  async processCourseMaterial(formData) {
    return api.postForm("/api/v1/course-materials/process", formData);
  },

  // 查询任务状态
  async getTaskStatus(taskId) {
    return api.get(`/api/v1/course-materials/tasks/${taskId}/status`);
  },

  // 清理指定材料
  async cleanupMaterial(courseId, courseMaterialId, options = {}) {
    const params = new URLSearchParams(options).toString();
    const url = `/api/v1/course-materials/${courseId}/${courseMaterialId}${
      params ? "?" + params : ""
    }`;
    return api.delete(url);
  },

  // 清理整个课程
  async cleanupCourse(courseId, options = {}) {
    const params = new URLSearchParams(options).toString();
    const url = `/api/v1/course-materials/course/${courseId}${
      params ? "?" + params : ""
    }`;
    return api.delete(url);
  },

  // 健康检查
  async getHealth() {
    return api.get("/api/v1/course-materials/health");
  },
};

// 任务轮询工具
class TaskPoller {
  constructor(apiFunction, taskId, onUpdate, onComplete, onError) {
    this.apiFunction = apiFunction;
    this.taskId = taskId;
    this.onUpdate = onUpdate;
    this.onComplete = onComplete;
    this.onError = onError;
    this.intervalId = null;
    this.isPolling = false;
  }

  start(interval = 2000) {
    if (this.isPolling) return;

    this.isPolling = true;
    this.poll();
    this.intervalId = setInterval(() => this.poll(), interval);
  }

  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isPolling = false;
  }

  async poll() {
    try {
      const result = await this.apiFunction(this.taskId);

      if (this.onUpdate) {
        this.onUpdate(result);
      }

      // 检查任务是否完成
      if (result.status === "completed" || result.status === "failed") {
        this.stop();
        if (this.onComplete) {
          this.onComplete(result);
        }
      }
    } catch (error) {
      console.error("任务轮询错误:", error);
      this.stop();
      if (this.onError) {
        this.onError(error);
      }
    }
  }
}

// 文件上传工具
class FileUploader {
  constructor(fileInput, options = {}) {
    this.fileInput = fileInput;
    this.selectedFile = null; // 存储选中的文件
    this.options = {
      maxSize: 10 * 1024 * 1024, // 10MB
      allowedTypes: [".md", ".txt"],
      onProgress: null,
      onSuccess: null,
      onError: null,
      ...options,
    };
    this.setupEventListeners();
  }

  setupEventListeners() {
    this.fileInput.addEventListener("change", (e) => {
      this.handleFileSelect(e.target.files);
    });
  }

  handleFileSelect(files) {
    if (files.length === 0) return;

    const file = files[0];

    // 验证文件
    if (!this.validateFile(file)) {
      return;
    }

    // 存储选中的文件
    this.selectedFile = file;

    // 触发成功回调
    if (this.options.onSuccess) {
      this.options.onSuccess(file);
    }
  }

  // 获取选中的文件
  getSelectedFile() {
    // 优先返回拖拽选择的文件，否则返回input选择的文件
    return (
      this.selectedFile ||
      (this.fileInput.files.length > 0 ? this.fileInput.files[0] : null)
    );
  }

  validateFile(file) {
    // 检查文件大小
    if (file.size > this.options.maxSize) {
      const maxSizeMB = this.options.maxSize / (1024 * 1024);
      if (this.options.onError) {
        this.options.onError(`文件大小超过限制 (${maxSizeMB}MB)`);
      }
      return false;
    }

    // 检查文件类型
    const fileExtension = "." + file.name.split(".").pop().toLowerCase();
    if (!this.options.allowedTypes.includes(fileExtension)) {
      if (this.options.onError) {
        this.options.onError(
          `不支持的文件类型，仅支持: ${this.options.allowedTypes.join(", ")}`
        );
      }
      return false;
    }

    return true;
  }

  // 创建FormData
  createFormData(file, additionalData = {}) {
    const formData = new FormData();
    formData.append("file", file);

    for (const [key, value] of Object.entries(additionalData)) {
      formData.append(key, value);
    }

    return formData;
  }
}

// 拖拽上传工具
class DragDropUploader extends FileUploader {
  constructor(dropZone, fileInput, options = {}) {
    super(fileInput, options);
    this.dropZone = dropZone;
    this.setupDragDropListeners();
  }

  setupDragDropListeners() {
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      this.dropZone.addEventListener(eventName, this.preventDefaults, false);
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      this.dropZone.addEventListener(
        eventName,
        () => {
          this.dropZone.classList.add("dragover");
        },
        false
      );
    });

    ["dragleave", "drop"].forEach((eventName) => {
      this.dropZone.addEventListener(
        eventName,
        () => {
          this.dropZone.classList.remove("dragover");
        },
        false
      );
    });

    this.dropZone.addEventListener(
      "drop",
      (e) => {
        const files = e.dataTransfer.files;
        this.handleFileSelect(files);
      },
      false
    );
  }

  preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
}
