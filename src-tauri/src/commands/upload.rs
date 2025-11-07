use crate::commands::file::validate_file_path;
use crate::models::response::UploadResponse;
use crate::services::http_client::get_http_client;
use reqwest::multipart::{Form, Part};
use std::fs::File;
use std::io::Read;

/// 文件上传命令
#[tauri::command]
pub async fn upload_file(file_path: String, api_url: String) -> Result<UploadResponse, String> {
    log::info!("上传文件: {}", file_path);

    // 验证文件路径
    let path = validate_file_path(&file_path).map_err(|e| e.to_string())?;

    // 读取文件
    let mut file = File::open(&path).map_err(|e| format!("文件读取失败: {}", e))?;

    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|e| format!("文件读取错误: {}", e))?;

    // 获取文件名
    let file_name = path
        .file_name()
        .unwrap()
        .to_string_lossy()
        .to_string();

    log::info!("文件大小: {} bytes", buffer.len());

    // 构建 multipart 表单
    let part = Part::bytes(buffer)
        .file_name(file_name.clone())
        .mime_str("application/octet-stream")
        .map_err(|e| format!("文件 MIME 设置失败: {}", e))?;

    let form = Form::new().part("file", part);

    // 发送 HTTP 请求
    let client = get_http_client();
    let upload_url = format!("{}/api/cad/upload", api_url);

    log::info!("上传到: {}", upload_url);

    let response = client
        .post(&upload_url)
        .multipart(form)
        .timeout(std::time::Duration::from_secs(60))
        .send()
        .await
        .map_err(|e| format!("上传请求失败: {}", e))?;

    // 检查响应状态
    if !response.status().is_success() {
        let status = response.status();
        let error_text = response
            .text()
            .await
            .unwrap_or_else(|_| "无法读取错误信息".to_string());
        return Err(format!("上传失败: HTTP {} - {}", status, error_text));
    }

    // 解析响应
    let upload_result: UploadResponse = response
        .json()
        .await
        .map_err(|e| format!("响应解析失败: {}", e))?;

    log::info!("上传成功, 任务ID: {}", upload_result.task_id);

    Ok(upload_result)
}
