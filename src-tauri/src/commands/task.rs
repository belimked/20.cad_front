use crate::models::response::{GeneratePdfResponse, TaskStatusResponse};
use crate::services::http_client::get_http_client;

/// 轮询任务状态命令
#[tauri::command]
pub async fn poll_task_status(
    task_id: String,
    api_url: String,
) -> Result<TaskStatusResponse, String> {
    log::debug!("查询任务状态: {}", task_id);

    let client = get_http_client();
    let status_url = format!("{}/api/tasks/{}/status", api_url, task_id);

    let response = client
        .get(&status_url)
        .timeout(std::time::Duration::from_secs(10))
        .send()
        .await
        .map_err(|e| format!("状态查询失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("查询失败: HTTP {}", response.status()));
    }

    let status: TaskStatusResponse = response
        .json()
        .await
        .map_err(|e| format!("状态解析失败: {}", e))?;

    log::debug!("任务状态: {:?}", status.status);

    Ok(status)
}

/// 生成 PDF 命令
#[tauri::command]
pub async fn generate_pdf(task_id: String, api_url: String) -> Result<GeneratePdfResponse, String> {
    log::info!("生成 PDF: 任务ID {}", task_id);

    let client = get_http_client();
    let pdf_url = format!("{}/api/cad/generate-pdf", api_url);

    let request_body = serde_json::json!({
        "task_id": task_id
    });

    let response = client
        .post(&pdf_url)
        .json(&request_body)
        .timeout(std::time::Duration::from_secs(30))
        .send()
        .await
        .map_err(|e| format!("PDF 生成请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("PDF 生成失败: HTTP {}", response.status()));
    }

    let pdf_info: GeneratePdfResponse = response
        .json()
        .await
        .map_err(|e| format!("响应解析失败: {}", e))?;

    log::info!("PDF 生成成功: {}", pdf_info.file_name);

    Ok(pdf_info)
}
