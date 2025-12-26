import os
import re
from urllib.parse import urlparse
import requests  # type: ignore
import pickle
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.common.exceptions import TimeoutException  # type: ignore
from cookies import save_cookies
from tqdm import tqdm  # type: ignore


def fetch_video_url(driver):
    """Fetches the video URL from the loaded page source."""
    print("Waiting for the video page to load...")
    try:
        video_element = driver.find_element(
            By.XPATH, "//source[contains(@type, 'video/mp4')]"
        )
        video_url = video_element.get_attribute("src")
        print(f"Found video URL: {video_url}")
        return video_url
    except Exception as e:
        print(f"Error locating video URL: {e}")
        return None


def folder_downloader(folder_url, driver, output_folder):
    """ Downloads all video files in a specified folder"""

    video_hrefs = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//turbo-frame[@id='videos-items']//div[starts-with(@id, 'video_')]"
            ))
        )
    except TimeoutException:
        print("No videos found after login; page may not have finished loading.")
        return

    video_divs = driver.find_elements(
        By.XPATH,
        "//turbo-frame[@id='videos-items']//div[starts-with(@id, 'video_')]"
    )

    for video in video_divs:
        a_element = video.find_element(By.TAG_NAME, 'a')
        href = a_element.get_attribute('href')
        video_hrefs.append(href)

    for href in video_hrefs:
        driver.get(href)
        video_url = fetch_video_url(driver)
        if os.path.exists(video_url):
            print(f"Video already exists: {video_url}")
            continue
        download_video_file(video_url, driver, output_folder)
        driver.get(folder_url)


def _safe_text(driver, xpath, fallback):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except Exception:
        return fallback


def _safe_attr(driver, xpath, attr, fallback=""):
    try:
        value = driver.find_element(By.XPATH, xpath).get_attribute(attr)
        return (value or "").strip() or fallback
    except Exception:
        return fallback


def _first_text(driver, xpaths):
    for xpath in xpaths:
        value = _safe_text(driver, xpath, "")
        if value:
            return value
    return ""


def _sanitize_filename(value, fallback):
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = cleaned.strip("._-")
    return cleaned or fallback


def _title_without_suffix(driver_title):
    if " - " in driver_title:
        return driver_title.split(" - ", 1)[0].strip()
    return driver_title.strip()


def _parent_from_url(driver):
    try:
        path = urlparse(driver.current_url).path.strip("/")
        if not path:
            return ""
        first_segment = path.split("/", 1)[0]
        return first_segment
    except Exception:
        return ""


def download_video_file(video_url, driver, output_folder):
    """Downloads the video file from the given URL."""

    save_cookies(driver)  # Save cookies for the requests session

    video_name = _first_text(
        driver,
        [
            "//div[contains(@class,'title-with-menu')]//h1",
            "//h1",
            "//main//header//h1",
        ],
    )
    if not video_name:
        video_name = _safe_attr(
            driver, "//meta[@property='og:title']", "content", ""
        )
    if not video_name:
        video_name = _title_without_suffix(driver.title or "")
    if not video_name:
        video_name = "video"

    parent_dir = _first_text(
        driver,
        [
            "//div[contains(@class,'title-with-menu')]"
            "//div[contains(@class,'headers')]//h2/a",
            "//nav[contains(@class,'breadcrumb')]//a[last()]",
            "//ol[contains(@class,'breadcrumb')]//a[last()]",
            "//a[contains(@href,'/channels/')][1]",
        ],
    )
    if not parent_dir:
        parent_dir = _safe_attr(
            driver, "//meta[@property='og:site_name']", "content", ""
        )
    if not parent_dir:
        parent_dir = _parent_from_url(driver)
    if not parent_dir:
        parent_dir = "switchtube"

    video_parentdir_name = _sanitize_filename(parent_dir, "switchtube")
    os.makedirs(
        os.path.join(output_folder, video_parentdir_name), exist_ok=True
    )
    video_filename = _sanitize_filename(video_name, "video") + ".mp4"
    video_path = os.path.join(
        output_folder, video_parentdir_name, video_filename
    )

    if os.path.exists(video_path):
        print(f"Video already exists: {video_path}")
        return

    session = requests.Session()

    # Load cookies into requests session
    with open("cookies.pkl", "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            session.cookies.set(
                cookie['name'], cookie['value'], domain=cookie['domain']
            )

    print(f"Downloading video from: {video_url}")
    response = session.get(video_url, stream=True)

    if response.status_code == 200:
        total_size = int(response.headers.get("content-length", 0))

        with open(video_path, "wb") as f, tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress_bar.update(len(chunk))

        print(f"\nVideo downloaded successfully: {video_path}")
    else:
        print(f"Failed to download video, status code: {response.status_code}")
