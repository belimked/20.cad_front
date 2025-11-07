use crate::models::response::{ApiResponse, TaskCreateData, UploadResponse};
use crate::services::http_client::get_http_client;
use serde::{Deserialize, Serialize};

/// 打印任务请求参数
#[derive(Debug, Serialize, Deserialize)]
struct PrintTaskRequest {
    dwg_url: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    config_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    callback_url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    use_bplot: Option<bool>,
}

/// 文件上传命令
///
/// 新的 API 接口：POST /api/v1/tasks/print
/// 提交 DWG 文件打印任务
#[tauri::command]
pub async fn upload_file(api_url: String, request_data: String) -> Result<UploadResponse, String> {
    log::info!("提交打印任务到: {}/api/v1/tasks/print", api_url);

    // 解析请求数据
    let request: PrintTaskRequest = serde_json::from_str(&request_data)
        .map_err(|e| format!("请求参数解析失败: {}", e))?;

    log::info!("DWG URL: {}", request.dwg_url);
    log::info!("Config: {:?}", request.config_name);
    log::info!("Use bplot: {:?}", request.use_bplot);

    // 发送 HTTP POST 请求
    let client = get_http_client();
    let print_url = format!("{}/api/v1/tasks/print", api_url);

    let response = client
        .post(&print_url)
        .json(&request)
        .timeout(std::time::Duration::from_secs(30))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    // 检查响应状态
    if !response.status().is_success() {
        let status = response.status();
        let error_text = response
            .text()
            .await
            .unwrap_or_else(|_| "无法读取错误信息".to_string());
        return Err(format!("提交任务失败: HTTP {} - {}", status, error_text));
    }

    // 解析响应 - 新格式包含 code, message, data
    let api_response: ApiResponse<TaskCreateData> = response
        .json()
        .await
        .map_err(|e| format!("响应解析失败: {}", e))?;

    // 检查业务状态码
    if api_response.code != 200 {
        return Err(format!(
            "任务创建失败: {} (code: {})",
            api_response.message, api_response.code
        ));
    }

    log::info!("任务创建成功, 任务ID: {}", api_response.data.task_id);

    // 转换为兼容格式返回给前端
    Ok(UploadResponse {
        task_id: api_response.data.task_id,
        message: api_response.message,
    })
}
