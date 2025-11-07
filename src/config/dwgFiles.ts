/**
 * DWG 文件配置
 * 预设的测试文件 URL 列表
 */

export interface DwgFileOption {
  id: string;
  name: string;
  displayName: string;
  url: string;
  description?: string;
}

/**
 * 文件服务器基础 URL
 * 可以通过环境变量覆盖
 */
const FILE_SERVER_BASE_URL = import.meta.env.VITE_FILE_SERVER_URL || 'http://10.3.19.199/cad';

/**
 * 预设的 DWG 文件列表
 */
export const DWG_FILE_OPTIONS: DwgFileOption[] = [
  {
    id: 'tz',
    name: 'tz.dwg',
    displayName: 'TZ 图纸',
    url: `${FILE_SERVER_BASE_URL}/tz.dwg`,
    description: '标准测试图纸',
  },
  {
    id: 'pcx2-1',
    name: 'PCX2.dwg',
    displayName: 'PCX2 图纸 #1',
    url: `${FILE_SERVER_BASE_URL}/PCX2.dwg`,
    description: 'PCX2 测试图纸',
  },
  {
    id: 'pcx2-2',
    name: 'PCX2.dwg',
    displayName: 'PCX2 图纸 #2',
    url: `${FILE_SERVER_BASE_URL}/PCX2.dwg`,
    description: 'PCX2 测试图纸（副本）',
  },
];

/**
 * 根据 ID 获取文件选项
 */
export function getDwgFileById(id: string): DwgFileOption | undefined {
  return DWG_FILE_OPTIONS.find((file) => file.id === id);
}

/**
 * 根据文件名获取文件选项
 */
export function getDwgFileByName(name: string): DwgFileOption[] {
  return DWG_FILE_OPTIONS.filter((file) => file.name === name);
}

/**
 * 构建自定义 DWG URL
 */
export function buildDwgUrl(fileName: string, customBaseUrl?: string): string {
  const baseUrl = customBaseUrl || FILE_SERVER_BASE_URL;
  return `${baseUrl}/${fileName}`;
}
