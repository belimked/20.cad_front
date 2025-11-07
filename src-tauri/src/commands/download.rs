use crate::services::http_client::get_http_client;
use futures_util::StreamExt;
use std::cmp::min;
use std::fs::File;
use std::io::Write;
use tauri::Window;

/// PDF 下载命令
#[tauri::command]
pub async fn download_pdf(
    window: Window,
    pdf_url: String,
    save_path: String,
) -> Result<String, String> {
    log::info!("下载 PDF: {} -> {}", pdf_url, save_path);

    let client = get_http_client();
    let response = client
        .get(&pdf_url)
        .send()
        .await
        .map_err(|e| format!("下载请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("下载失败: HTTP {}", response.status()));
    }

    let total_size = response.content_length().ok_or("无法获取文件大小")?;

    log::info!("文件大小: {} bytes", total_size);

    let mut file = File::create(&save_path).map_err(|e| format!("文件创建失败: {}", e))?;

    let mut downloaded: u64 = 0;
    let mut stream = response.bytes_stream();

    while let Some(item) = stream.next().await {
        let chunk = item.map_err(|e| format!("下载数据失败: {}", e))?;

        file.write_all(&chunk)
            .map_err(|e| format!("文件写入失败: {}", e))?;

        downloaded = min(downloaded + (chunk.len() as u64), total_size);

        // 计算进度百分比
        let progress = ((downloaded as f64 / total_size as f64) * 100.0) as u8;

        // 发送进度事件到前端
        window
            .emit("download-progress", progress)
            .map_err(|e| format!("进度事件发送失败: {}", e))?;
    }

    log::info!("下载完成: {}", save_path);

    Ok(save_path)
}
