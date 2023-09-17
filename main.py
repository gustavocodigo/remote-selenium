
from selenium import webdriver
from selenium.webdriver.chrome import service
from seleremote import SeleRemote

from selenium import webdriver


if __name__ == "__main__":
    try:
        webdriver_service = service.Service("./operadriver_linux64/operadriver")
        webdriver_service.start()
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_experimental_option('w3c', True)
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')  # Required for headless mode on Linux

        # Create a remote WebDriver instance
        driver = webdriver.Remote(webdriver_service.service_url, options=options)


        server = SeleRemote(driver)
        server.start_server()
    except KeyboardInterrupt:
        print("Server terminated by user")
