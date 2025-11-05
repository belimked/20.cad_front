#!/usr/bin/env python3
"""
PDF转图片后OCR识别
适用于文字被转为矢量路径的PDF文件
"""

import requests
import base64
import sys
from pathlib import Path
from typing import List, Optional
import subprocess
import tempfile
import os


class PDFImageOCR:
    """PDF通过图片方式进行OCR"""

    def __init__(self, umi_ocr_url: str = "http://10.3.19.63:11224"):
        self.umi_ocr_url = umi_ocr_url.rstrip('/')

    def check_dependencies(self) -> bool:
        """检查依赖工具"""
        # 检查 pdftoppm
        try:
            subprocess.run(
                ['pdftoppm', '-v'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 缺少 pdftoppm 工具")
            print("\n安装方法:")
            print("  macOS:   brew install poppler")
            print("  Ubuntu:  apt install poppler-utils")
            print("  CentOS:  yum install poppler-utils")
            return False

    def pdf_to_images(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        dpi: int = 300
    ) -> List[str]:
        """
        将PDF转换为图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录（None则使用临时目录）
            dpi: 分辨率（推荐300）

        Returns:
            生成的图片路径列表
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ PDF文件不存在: {pdf_path}")
            return []

        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n📄 转换PDF为图片: {pdf_file.name}")
        print(f"   DPI: {dpi}")

        # 使用 pdftoppm 转换
        prefix = output_path / "page"

        try:
            subprocess.run(
                [
                    'pdftoppm',
                    '-png',
                    '-r', str(dpi),
                    str(pdf_file),
                    str(prefix)
                ],
                check=True,
                capture_output=True
            )

            # 查找生成的图片
            images = sorted(output_path.glob("page-*.png"))

            print(f"   ✅ 生成 {len(images)} 张图片")
            return [str(img) for img in images]

        except subprocess.CalledProcessError as e:
            print(f"   ❌ 转换失败: {e.stderr.decode()}")
            return []

    def ocr_image(
        self,
        image_path: str,
        return_format: str = "text"
    ) -> Optional[str]:
        """
        对单张图片进行OCR

        Args:
            image_path: 图片路径
            return_format: 返回格式（text/dict）

        Returns:
            识别结果
        """
        with open(image_path, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode()

        url = f"{self.umi_ocr_url}/api/ocr"

        try:
            response = requests.post(
                url,
                json={
                    'base64': img_base64,
                    'options': {
                        'data.format': return_format,
                        'ocr.limit_side_len': 4320  # 高精度
                    }
                },
                timeout=60
            )

            result = response.json()

            if result.get('code') == 100:
                return result.get('data', '')
            elif result.get('code') == 101:
                # 未识别到文字
                return ''
            else:
                print(f"   ⚠️ OCR失败: {result.get('data', '未知错误')}")
                return None

        except Exception as e:
            print(f"   ❌ OCR异常: {e}")
            return None

    def process_pdf(
        self,
        pdf_path: str,
        output_txt: Optional[str] = None,
        dpi: int = 300,
        keep_images: bool = False
    ) -> Optional[str]:
        """
        完整处理PDF（转图片→OCR→合并文本）

        Args:
            pdf_path: PDF文件路径
            output_txt: 输出文本文件路径（None则只返回文本）
            dpi: 图片分辨率
            keep_images: 是否保留中间图片

        Returns:
            提取的文本内容
        """
        # 检查依赖
        if not self.check_dependencies():
            return None

        # 转换为图片
        temp_dir = None if keep_images else tempfile.mkdtemp()
        images = self.pdf_to_images(pdf_path, temp_dir, dpi)

        if not images:
            return None

        # OCR每张图片
        print(f"\n🔍 OCR识别中...")

        all_text = []
        for i, img_path in enumerate(images, 1):
            print(f"   [{i}/{len(images)}] {Path(img_path).name}...", end=' ')

            text = self.ocr_image(img_path, return_format='text')

            if text is not None:
                char_count = len(text) if isinstance(text, str) else len(str(text))
                print(f"✅ {char_count} 字符")
                all_text.append(f"# 第 {i} 页\n\n{text}")
            else:
                print(f"❌")

        # 合并文本
        full_text = '\n\n' + '='*60 + '\n\n'.join(all_text)

        # 保存到文件
        if output_txt:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"\n✅ 文本已保存: {output_txt}")

        # 清理临时图片
        if not keep_images and temp_dir:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"   🗑️  清理临时图片")

        return full_text


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  {sys.argv[0]} <PDF文件> [输出文本文件] [DPI]")
        print("\n示例:")
        print(f"  {sys.argv[0]} input.pdf")
        print(f"  {sys.argv[0]} input.pdf output.txt")
        print(f"  {sys.argv[0]} input.pdf output.txt 600")
        print("\n说明:")
        print("  DPI: 图片分辨率（默认300，高精度可用600）")
        print("  注意: 需要先安装 poppler-utils")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_txt = sys.argv[2] if len(sys.argv) > 2 else None
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 300

    processor = PDFImageOCR()

    text = processor.process_pdf(
        pdf_path,
        output_txt=output_txt,
        dpi=dpi,
        keep_images=False
    )

    if text and not output_txt:
        # 如果没有指定输出文件，打印到控制台
        print("\n" + "="*60)
        print("识别结果:")
        print("="*60)
        print(text)


if __name__ == "__main__":
    main()
