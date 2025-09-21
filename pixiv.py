import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 设置Chrome无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
chrome_options.add_argument("--no-sandbox")  # 禁用沙盒
chrome_options.add_argument("--disable-images")

# 初始化浏览器（放在循环外部）
driver = webdriver.Chrome(options=chrome_options)
rq = '20250813'
try:
    response = requests.get("https://www.pixiv.net/ranking.php?mode=daily&date="+rq)
    soup = BeautifulSoup(response.text, "html.parser")
    all_sections = soup.find_all('div', class_='ranking-image-item')

    # 首先设置Cookie（只需要设置一次）
    driver.get("https://www.pixiv.net")
    cookie = {'name': 'first_visit_datetime_pc', 'value': '2025-06-25%2018%3A09%3A45', 'domain': '.pixiv.net'}
    driver.add_cookie(cookie)

    for i, section in enumerate(all_sections):
        try:
            lj = section.find("a").get('href')
            lj2 = 'https://www.pixiv.net' + lj
            print(f"正在处理第 {i + 1} 个作品: {lj2}")

            # 访问目标页面
            driver.get(lj2)

            # 使用智能等待而不是固定时间等待
            wait = WebDriverWait(driver, 10)

            # 直接等待图片元素出现
            img_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='i.pximg.net'][src*='master1200']"))
            )

            img_url = img_element.get_attribute("src")
            print("图片URL:", img_url)

            # 下载图片
            url = img_url.replace("i.pximg.net", "i.yuki.sh")
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
                "referer": "https://www.pixiv.net/"
            }
            img_name = url.split('/')[-1]
            img_dir = "pixiv_images/"
            img_path = img_dir + img_name

            if not os.path.exists(img_dir):
                os.makedirs(img_dir)

            # 检查文件是否已存在，避免重复下载
            if not os .path.exists(img_path):
                data = requests.get(url, headers=headers)
                if data.status_code == 200:
                    with open(img_path, "wb") as f:
                        f.write(data.content)
                    print(f'{data.status_code} - {img_name} 下载完成\n')
                else:
                    print(f'下载失败，状态码: {data.status_code}\n')
            else:
                print(f'{img_name} 已存在，跳过下载\n')

        except Exception as e:
            print(f"处理第 {i + 1} 个作品时出错: {str(e)}\n")
            continue
finally:
    # 在所有循环结束后关闭浏览器（放在循环外部）
    driver.quit()
    print("所有任务完成，浏览器已关闭")