use serde::{Deserialize, Serialize};

/// 标准 API 响应包装器
#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub code: i32,
    pub message: String,
    pub data: T,
}

/// 任务创建响应数据
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskCreateData {
    pub task_id: String,
    pub status: String, // "pending" | "queued" | "processing" | "completed" | "failed"
    pub created_at: String,
}

/// 文件上传响应(向前兼容,从 ApiResponse 中提取)
#[derive(Debug, Serialize, Deserialize)]
pub struct UploadResponse {
    pub task_id: String,
    pub message: String,
}

/// 任务状态响应
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskStatusResponse {
    pub task_id: String,
    pub status: String, // "queued" | "processing" | "completed" | "failed"
    pub progress: u8,   // 0-100
    pub message: Option<String>,
}

/// PDF 生成响应
#[derive(Debug, Serialize, Deserialize)]
pub struct GeneratePdfResponse {
    pub pdf_id: String,
    pub file_name: String,
    pub download_url: String,
    pub file_size: Option<u64>,
}

/// 任务步骤
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskStep {
    #[serde(alias = "step_id")]
    pub step_order: i32,
    pub step_name: String,
    pub status: String, // "pending" | "running" | "completed" | "failed"
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    #[serde(alias = "duration")]
    pub duration_seconds: Option<f64>,
    #[serde(alias = "log_message")]
    pub message: Option<String>,
    pub error_message: Option<String>,
}

/// 任务详情响应
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskDetailResponse {
    pub task_id: String,
    pub dwg_url: String,
    #[serde(default)]
    pub dwg_filename: Option<String>,
    #[serde(default)]
    pub local_path: Option<String>,
    #[serde(default)]
    pub file_size: Option<i64>,
    pub config_name: String,
    pub use_bplot: bool,
    pub status: String, // "queued" | "processing" | "completed" | "failed"
    pub progress: u8,   // 0-100
    #[serde(default)]
    pub current_step: Option<String>,
    pub created_at: String,
    #[serde(default)]
    pub updated_at: Option<String>,
    #[serde(default)]
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub error_message: Option<String>,
    pub steps: Vec<TaskStep>,
}
