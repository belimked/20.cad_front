use serde::{Deserialize, Serialize};

/// 任务历史记录
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskHistory {
    pub task_id: String,
    pub file_name: String,
    pub file_size: u64,
    pub upload_time: String,
    pub completion_time: Option<String>,
    pub status: String,
    pub error_message: Option<String>,
    pub pdf_file_url: Option<String>,
}

/// 保存任务历史命令
#[tauri::command]
pub async fn save_task_history(tasks: Vec<TaskHistory>) -> Result<(), String> {
    log::info!("保存任务历史: {} 条", tasks.len());

    // 注意：实际存储操作由前端的 tauri-plugin-store 处理
    // 这里仅作为示例，实际可能不需要这个命令
    Ok(())
}

/// 加载任务历史命令
#[tauri::command]
pub async fn load_task_history() -> Result<Vec<TaskHistory>, String> {
    log::info!("加载任务历史");

    // 注意：实际存储操作由前端的 tauri-plugin-store 处理
    // 这里仅作为示例，实际可能不需要这个命令
    Ok(vec![])
}

/// 清除历史命令
#[tauri::command]
pub async fn clear_history() -> Result<(), String> {
    log::info!("清除任务历史");

    // 注意：实际存储操作由前端的 tauri-plugin-store 处理
    Ok(())
}
