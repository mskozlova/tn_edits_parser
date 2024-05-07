import re
import requests


def get_html(user_id, cookie):
    url = f"https://tech-nation-visa.smapply.io/rend/{user_id}/dt/?is_applicant=True"
    
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookie,
        'Referer': f'https://tech-nation-visa.smapply.io/sub/{user_id}/sprv/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    r = requests.get(
        url=url,
        headers=headers
    )
    r.raise_for_status()
    return r.json().get("html", "")
  

def parse_last_edited(html):
    prefix = "<strong>Last edited:</strong>"
    postfix = "</small>"
    if prefix in html:
        last_edited_time = re.findall(f"{prefix}([^<]+){postfix}", html)
        if len(last_edited_time) != 1:
            raise ValueError(f"Error while parsing edit time. No time found or multiple times found. HTML: {html}")
        return last_edited_time[0].strip()

    raise ValueError(f"Unexpected HTML format. 'Last edited' not found. HTML: {html}")
