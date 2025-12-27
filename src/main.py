from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.chrome.service import Service  # type: ignore
# from cookies import load_cookies, save_cookies, is_authenticated
from downloader import fetch_video_url, download_video_file, folder_downloader
from authentication import authenticate_user
import os
import argparse
import sys
from dotenv import find_dotenv, load_dotenv  # type: ignore


def load_environment_variables():
    """Loads environment variables."""
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path=dotenv_path, override=True)
    school = os.getenv("SCHOOL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    if not all([school, username, password]):
        print("Error: Missing one or more environment variables.")
    return username, password, school


def setup_selenium_driver(debug):
    """Sets up a headless Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    if not debug:
        chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def main(
    url, username, password, school,
    debug=False, output_folder="downloads"
):
    """Main function to execute the video download process."""

    driver = setup_selenium_driver(debug)

    try:
        driver.get(url)

        # # Load cookies if available and attempt access
        # if load_cookies(driver):
        #     driver.get(url)
        #     if is_authenticated(driver):
        #         print("Authenticated with cookies.")
        #     else:
        #         print("Cookies invalid, proceeding with login...")
        #         authenticate_user(driver, url, username, password, school)
        #         save_cookies(driver)  # Save cookies after authentication
        # else:
        # If no cookies found, authenticate
        # print("No cookies found, proceeding with login...")
        authenticate_user(driver, url, username, password, school)
        # save_cookies(driver)  # Save cookies after authentication

        if "channels" in url:
            folder_downloader(url, driver, output_folder)
        elif "videos" in url:
            video_url = fetch_video_url(driver)

            if video_url:
                download_video_file(video_url, driver, output_folder)
            else:
                print("Video URL not found. Exiting.")
        else:
            print("Invalid URL. Exiting.")
            return
    finally:
        print("quit driver")
        driver.quit()


# Example usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download videos from SWITCHtube."
    )
    parser.add_argument("url", help="URL of the video or folder to download.")
    parser.add_argument('-u', '--user', help="username")
    parser.add_argument('-p', '--password', help="password")
    parser.add_argument('-s', '--school', help='match university name')
    parser.add_argument(
        '-d', '--dir',
        default="downloads",
        help="directory to download videos"
    )
    parser.add_argument(
        '--debug', action='store_true',
        help="disable headless mode showing browser window"
    )
    args = parser.parse_args()

    env_username, env_password, env_school = load_environment_variables()
    username = args.user or env_username
    password = args.password or env_password
    school = args.school or env_school

    if not all([username, password, school]):
        print("Error: Missing one or more credentials (username, password, school).")
        sys.exit(1)

    main(args.url, username, password, school, args.debug, args.dir)
