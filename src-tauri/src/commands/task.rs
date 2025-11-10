use crate::models::response::{ApiResponse, GeneratePdfResponse, TaskDetailResponse, TaskStatusResponse, TaskStep};
use crate::services::http_client::get_http_client;

/// 按 started_at 时间对步骤进行排序
/// 如果 started_at 为 None,则放到最后
fn sort_steps_by_time(steps: &mut Vec<TaskStep>) {
    steps.sort_by(|a, b| {
        match (&a.started_at, &b.started_at) {
            (Some(time_a), Some(time_b)) => time_a.cmp(time_b),
            (Some(_), None) => std::cmp::Ordering::Less,  // 有时间的排前面
            (None, Some(_)) => std::cmp::Ordering::Greater, // 无时间的排后面
            (None, None) => a.step_order.cmp(&b.step_order), // 都无时间则按 step_order
        }
    });
}

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

/// 查询任务详情命令（新 API）
/// GET /api/v1/tasks/{task_id}
#[tauri::command]
pub async fn get_task_detail(
    task_id: String,
    api_url: String,
) -> Result<TaskDetailResponse, String> {
    log::debug!("查询任务详情: {}", task_id);

    let client = get_http_client();
    let detail_url = format!("{}/api/v1/tasks/{}", api_url, task_id);

    let response = client
        .get(&detail_url)
        .timeout(std::time::Duration::from_secs(10))
        .send()
        .await
        .map_err(|e| format!("任务详情查询失败: {}", e))?;

    if !response.status().is_success() {
        let status = response.status();
        let error_text = response
            .text()
            .await
            .unwrap_or_else(|_| "无法读取错误信息".to_string());
        return Err(format!("查询失败: HTTP {} - {}", status, error_text));
    }

    // 尝试解析新格式(带 ApiResponse 包装器)
    let response_text = response
        .text()
        .await
        .map_err(|e| format!("响应读取失败: {}", e))?;

    // 尝试解析为 ApiResponse 格式
    if let Ok(api_response) = serde_json::from_str::<ApiResponse<TaskDetailResponse>>(&response_text) {
        // 新格式: { code, message, data }
        if api_response.code != 200 {
            return Err(format!(
                "查询失败: {} (code: {})",
                api_response.message, api_response.code
            ));
        }
        log::debug!("任务状态: {:?}, 进度: {}%", api_response.data.status, api_response.data.progress);

        // 对步骤按 started_at 时间排序
        let mut data = api_response.data;
        sort_steps_by_time(&mut data.steps);

        return Ok(data);
    }

    // 尝试解析为旧格式(直接返回 TaskDetailResponse)
    if let Ok(mut detail) = serde_json::from_str::<TaskDetailResponse>(&response_text) {
        // 旧格式: 直接返回详情对象
        log::debug!("任务状态: {:?}, 进度: {}%", detail.status, detail.progress);

        // 对步骤按 started_at 时间排序
        sort_steps_by_time(&mut detail.steps);

        return Ok(detail);
    }

    // 两种格式都解析失败
    Err(format!("响应解析失败: 未知的响应格式"))
}
