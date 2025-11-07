use crate::error::AppError;
use std::path::PathBuf;
use tauri::api::dialog::FileDialogBuilder;

/// 选择文件命令
#[tauri::command]
pub async fn select_file() -> Result<String, String> {
    log::info!("调用 select_file 命令");

    let file_path = tauri::async_runtime::spawn(async move {
        let (tx, rx) = std::sync::mpsc::channel();

        FileDialogBuilder::new()
            .add_filter("DWG Files", &["dwg"])
            .set_title("选择 CAD 文件")
            .pick_file(move |path| {
                tx.send(path).ok();
            });

        rx.recv().ok().flatten()
    })
    .await
    .map_err(|e| format!("文件选择失败: {}", e))?;

    match file_path {
        Some(path) => {
            let path_str = path.to_string_lossy().to_string();
            log::info!("文件选择成功: {}", path_str);
            Ok(path_str)
        }
        None => {
            log::warn!("用户取消文件选择");
            Err("未选择文件".to_string())
        }
    }
}

/// 在文件管理器中打开文件位置
#[tauri::command]
pub async fn open_file_location(file_path: String) -> Result<(), String> {
    log::info!("打开文件位置: {}", file_path);

    let path = PathBuf::from(&file_path);

    if !path.exists() {
        return Err("文件不存在".to_string());
    }

    // 获取父目录
    let parent = path.parent().ok_or("无法获取父目录")?;

    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("explorer")
            .arg(parent)
            .spawn()
            .map_err(|e| format!("打开文件夹失败: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        std::process::Command::new("open")
            .arg(parent)
            .spawn()
            .map_err(|e| format!("打开文件夹失败: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        std::process::Command::new("xdg-open")
            .arg(parent)
            .spawn()
            .map_err(|e| format!("打开文件夹失败: {}", e))?;
    }

    Ok(())
}

/// 验证文件路径
pub fn validate_file_path(path: &str) -> Result<PathBuf, AppError> {
    let path_buf = PathBuf::from(path);

    // 检查文件是否存在
    if !path_buf.exists() {
        return Err(AppError::Custom("文件不存在".to_string()));
    }

    // 检查扩展名
    if path_buf.extension().and_then(|s| s.to_str()) != Some("dwg") {
        return Err(AppError::Custom("仅支持 DWG 文件".to_string()));
    }

    // 规范化路径（防止路径遍历）
    let canonical = path_buf
        .canonicalize()
        .map_err(|e| AppError::Custom(format!("路径解析失败: {}", e)))?;

    Ok(canonical)
}
