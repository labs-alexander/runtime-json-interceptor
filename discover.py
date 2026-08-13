import json
import logging
import threading
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
logging.basicConfig(
	level=logging.DEBUG
	)
ALL_RESPONSES = []
TERM_HOLDER = {"value": None}
print_lock = threading.Lock()

def main():
	with sync_playwright() as p:
		url = input("What site do you want to browse?")
		url = "https://www." + url if not url.startswith("https://www.") else url
		logger.debug("Your url %s", url)
		page, context = setup_browser(p)
		page.on("response", handle_response)
		page.goto(url)

		stop_event = threading.Event()
		input_thread = threading.Thread(target=wait_input, args=(stop_event,), daemon=True)
		input_thread.start()
		while not stop_event.is_set():
			page.wait_for_timeout(100)

		context.close()


def setup_browser(p):
	context = p.chromium.launch_persistent_context(
		headless=False,
		args=["--disable-blink-features=AutomationControlled"],
		user_data_dir="./fix_cookies"
		)
	context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
	page = context.pages[0] if context.pages else context.new_page()
	return page, context


def handle_response(response):
	if not response.headers.get("content-type") == "application/json":
		return
	try:	
		ALL_RESPONSES.append(response.json())
	except Exception:
		return


def wait_input(stop_event):
	while not stop_event.is_set():
		cmd = input("1.CLOSE")
		if cmd == "1":
			stop_event.set()

		else:
			search_all(cmd):



def find_element(term, response):
	if isinstance(response, (str, int, bool, float)):
		if str(term).lower() in str(response).lower():
			return response

	elif isinstance(response, list):
		for i in response:
			if result := find_element(term, i):
				return result 

	elif isinstance(response, dict):
		for v in response.values():
			if result := find_element(term, v):
				return result 


def search_all(term):
	for response_body in ALL_RESPONSES:
		if result := find_element(term, response_body):
			print(result)


if __name__ == "__main__":
	main()
