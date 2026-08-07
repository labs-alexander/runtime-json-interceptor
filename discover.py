import time
import threading
from playwright.sync_api import sync_playwright

def handle_response(response, search_term):
    try:
        url = response.url
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return
        try:
        	data = response.json()
        	body = response.text()[:1000]
        except Exception:
        	return
        if result := find_element(search_term, data):
        	print(f"\n[DADO RECOLHIDO]\nURL: {url}\nBody: {body}\n---", flush=True)
        	print(f"Encontrado em {response.url}: {result}")
    except Exception:
        pass

def find_element(term, element):
	if isinstance(element, dict):
		for k, v in element.items():
			if result := find_element(term, v):
				return result
	elif isinstance(element, list):
		for item in element:
			if result := find_element(term, item):
				return result
	elif isinstance(element, (str, int, bool, float)):
		if str(term).lower() in str(element).lower():
			return element

if __name__ == "__main__":
    target_url = input("Qual site você quer investigar? ")
    search_term = input("O que você quer encontrar? ")
    stop_event = threading.Event()
    def wait_input():
        input("Pressione Enter para encerrar...\n")
        stop_event.set()
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_context",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.pages[0] if context.pages else context.new_page()

        page.on("response", lambda r: handle_response(r, search_term))
        page.goto(target_url)
        threading.Thread(target=wait_input, daemon=True).start()
        while not stop_event.is_set():
            try:
                page.wait_for_timeout(100)
            except Exception:
                break
        context.close()
