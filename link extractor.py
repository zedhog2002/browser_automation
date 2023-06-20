import time
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from playwright.sync_api import Playwright, sync_playwright

useragent = UserAgent()


def run(playwright: Playwright, place: str, thing: str) -> None:
    browser_type = playwright.chromium
    browser = browser_type.launch(headless=False)
    context = browser.new_context(user_agent=f"{useragent}")
    page = context.new_page()
    page.goto(f"https://www.justdial.com/{place}/{thing}/")
    first_close = page.query_selector('.white_close_icon')
    first_close.click()
    element = page.query_selector('.jsx-6ab5af3a8693e5db.resfilter_item.gray_whitefill_animat')
    element.click()
    element = page.query_selector('span.animtext:has-text("Rating")')
    element.click()

    scroll_height = page.evaluate("document.documentElement.scrollHeight")
    scroll_position = 200
    scroll_step = 200

    while scroll_position < scroll_height:
        window_height = page.evaluate("window.innerHeight")
        page.evaluate(f"window.scrollTo(0, {scroll_position})")
        time.sleep(1)
        scroll_position += scroll_step
        scroll_height = page.evaluate("document.documentElement.scrollHeight")
        if page.query_selector('#onCloseMobile'):
            close_popup = page.query_selector('#onCloseMobile')
            close_popup.click()

    div_heights = []
    divs = page.query_selector_all('.resultbox')
    for div_number, div in enumerate(divs, start=1):
        div_height = div.evaluate('(el) => el.offsetHeight')
        div_heights.append(div_height)

        cumulative_height = sum(div_heights[:div_number]) + 200
        page.evaluate(f"window.scrollTo(0, {cumulative_height})")
        time.sleep(0.1)
        # Perform your operations with the buttons within the div
        buttons = div.query_selector_all('.button_flare')
        for button in buttons:
            button.click()
            time.sleep(1)
            contact_modal = page.query_selector('.jd_modal_content')
            if contact_modal:
                modal_html = contact_modal.inner_html()
                modal_soup = BeautifulSoup(modal_html, 'html.parser')
                phone_numbers = modal_soup.find_all('a', class_='color111')
                numbers = []
                for number in phone_numbers:
                    phone_number = number.text.strip()
                    numbers.append((div_number, phone_number))
                print(numbers)

                close_button = contact_modal.query_selector('.jd_modal_close')
                close_button.click()

    page_html = page.content()
    soup = BeautifulSoup(page_html, 'html.parser')

    # extract title of shop
    results_title = soup.find_all('h2', class_='resultbox_title')
    titles = [result.get_text(strip=True) for result in results_title]

    # extract the address of shop
    results_address = soup.find_all('div', class_='resultbox_address')
    addresses = [result.get_text(strip=True) for result in results_address]

    results_number = soup.find_all('span', class_='callcontent')
    numbers = [result.get_text(strip=True) for result in results_number]

    # # Ensure arrays have the same length
    # max_length = max(len(titles), len(addresses), len(numbers))
    # titles += [''] * (max_length - len(titles))
    # addresses += [''] * (max_length - len(addresses))
    # numbers += [''] * (max_length - len(numbers))

    # Combine data in dataframe
    data = {
        'Title': titles,
        'Address': addresses,
        'Numbers': numbers
    }

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Sort the DataFrame by 'Title' column in alphabetical order
    df_sorted = df.sort_values('Title')

    # Write the sorted data to the CSV file
    filename = f'{place}_{thing}_data.csv'
    df_sorted.to_csv(filename, index=False, encoding='utf-8')

    print(f"Data saved to '{filename}'")

    browser.close()


with sync_playwright() as playwright:
    run(playwright, 'Mumbai', 'Chemists')
