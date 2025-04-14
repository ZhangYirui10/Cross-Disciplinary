import json
import os
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import time

def download_image(url, save_path):
    """下载单个图片"""
    try:
        # 创建请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Successfully downloaded: {save_path}")
            return True
        else:
            print(f"Failed to download {url}: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def main():
    # 创建保存图片的目录
    image_dir = "professor_images"
    os.makedirs(image_dir, exist_ok=True)
    
    # 读取JSON文件
    with open('data/nus_faculty_with_openalex_id.json', 'r') as f:
        professors = json.load(f)
    
    # 统计信息
    total = len(professors)
    success = 0
    failed = 0
    
    # 使用线程池并行下载
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        
        for prof in professors:
            if not prof.get('pic'):
                print(f"No image URL for professor: {prof.get('name', 'Unknown')}")
                continue
                
            # 从URL中提取文件名
            url = prof['pic']
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"{prof['socid']}.jpg"
                
            save_path = os.path.join(image_dir, filename)
            
            # 如果文件已经存在，跳过下载
            if os.path.exists(save_path):
                print(f"Image already exists: {save_path}")
                success += 1
                continue
                
            # 提交下载任务
            future = executor.submit(download_image, url, save_path)
            futures.append(future)
            
            # 添加小延迟，避免请求过于频繁
            time.sleep(0.1)
        
        # 等待所有下载完成
        for future in futures:
            if future.result():
                success += 1
            else:
                failed += 1
    
    # 打印统计信息
    print("\nDownload Summary:")
    print(f"Total professors: {total}")
    print(f"Successfully downloaded: {success}")
    print(f"Failed to download: {failed}")
    print(f"Images saved in: {os.path.abspath(image_dir)}")

if __name__ == "__main__":
    main() 