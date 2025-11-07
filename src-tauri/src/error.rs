use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("文件操作错误: {0}")]
    FileError(#[from] std::io::Error),

    #[error("网络请求错误: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("JSON 解析错误: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("Tauri 错误: {0}")]
    TauriError(String),

    #[error("自定义错误: {0}")]
    Custom(String),
}

// 转换为前端友好的错误字符串
impl From<AppError> for String {
    fn from(err: AppError) -> String {
        err.to_string()
    }
}

// Tauri 错误转换
impl From<tauri::Error> for AppError {
    fn from(err: tauri::Error) -> Self {
        AppError::TauriError(err.to_string())
    }
}
