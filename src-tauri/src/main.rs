// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod error;
mod models;
mod services;

use commands::{download, file, storage, task, upload};

fn main() {
    // 初始化日志
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();

    log::info!("应用启动");

    tauri::Builder::default()
        .plugin(tauri_plugin_store::Builder::default().build())
        .invoke_handler(tauri::generate_handler![
            // 文件操作命令
            file::select_file,
            file::open_file_location,
            // 上传命令
            upload::upload_file,
            // 任务查询命令
            task::poll_task_status,
            task::generate_pdf,
            // 下载命令
            download::download_pdf,
            // 存储命令
            storage::save_task_history,
            storage::load_task_history,
            storage::clear_history,
        ])
        .setup(|_app| {
            #[cfg(debug_assertions)]
            {
                use tauri::Manager;
                let window = _app.get_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
