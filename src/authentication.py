from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait, Select  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type:ignore
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # type: ignore
from selenium.webdriver.common.keys import Keys  # type: ignore


def _xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"


def _select_school_from_dropdown(driver, school: str) -> bool:
    try:
        select_element = driver.find_element(By.ID, "userIdPSelection")
    except NoSuchElementException:
        return False

    select = Select(select_element)
    for option in select_element.find_elements(By.TAG_NAME, "option"):
        option_value = (option.get_attribute("value") or "").strip()
        option_text = option.text.strip()
        if option_value == school:
            select.select_by_value(option_value)
            return True
        if option_text == school or school in option_text:
            select.select_by_visible_text(option_text)
            return True
    return False


def _select_school_from_list(driver, selection_input, school: str) -> None:
    selection_input.click()
    selection_input.send_keys(Keys.COMMAND, "a")
    selection_input.send_keys(Keys.BACKSPACE)
    selection_input.send_keys(school)

    xpath_school = _xpath_literal(school)
    option_xpath = (
        "//*[contains(@class,'idd_listItem') or contains(@class,'idd_li')]"
        f"[(@savedvalue = {xpath_school}) or (@data = {xpath_school})"
        f" or contains(@data, {xpath_school}) or normalize-space(.) = {xpath_school}"
        f" or contains(normalize-space(.), {xpath_school})]"
    )
    try:
        option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        option.click()
    except TimeoutException:
        selection_input.send_keys(Keys.ENTER)


def authenticate_user(driver, url, username, password, school):
    """Authenticates the user on the website."""
    print(f"Opening URL: {url}")
    driver.get(url)

    try:
        selection_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "userIdPSelection_iddtext"))
        )
        if _select_school_from_dropdown(driver, school):
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}))",
                driver.find_element(By.ID, "userIdPSelection"),
            )
        else:
            _select_school_from_list(driver, selection_input, school)
        try:
            driver.find_element(By.NAME, "Select").click()
        except NoSuchElementException:
            pass

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(username)
        driver.find_element(By.ID, "button-submit").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        ).send_keys(password)
        driver.find_element(By.ID, "button-proceed").click()

        try:
            otp_input = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.ID, "otp"))
            )
            otp_code = input("Enter one-time password (OTP) code: ").strip()
            otp_input.send_keys(otp_code)
            try:
                driver.find_element(By.ID, "button-submit").click()
            except NoSuchElementException:
                otp_input.send_keys(Keys.ENTER)
        except TimeoutException:
            pass
        print("User authenticated.")
    except Exception as e:
        print(f"Authentication failed: {e}")
