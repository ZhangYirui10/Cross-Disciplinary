from playwright.sync_api import sync_playwright, TimeoutError

def get_research_interests(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("#res_interest li", timeout=10000)
                items = page.query_selector_all("#res_interest li")
                interests = [item.inner_text() for item in items]
            except TimeoutError:
                print(f"⏱️ 页面加载超时：{url}")
                interests = []
            except Exception as e:
                print(f"⚠️ 加载失败：{url}，错误信息：{e}")
                interests = []
            finally:
                browser.close()
    except Exception as e:
        print(f"❌ 浏览器启动失败或未知错误：{url}，错误信息：{e}")
        interests = []

    return interests