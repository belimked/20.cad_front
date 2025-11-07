use serde::{Deserialize, Serialize};

/// 文件上传响应
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
