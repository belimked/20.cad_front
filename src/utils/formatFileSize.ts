/**
 * 格式化文件大小为人类可读的字符串
 * @param bytes 文件大小(字节)
 * @returns 格式化后的字符串 (例如: "1.5 MB")
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));

  const value = bytes / Math.pow(k, i);

  // 对于字节单位,不显示小数点
  const formatted = i === 0 ? value.toFixed(0) : value.toFixed(1);

  return `${formatted} ${sizes[i]}`;
}

