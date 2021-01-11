import re
import urllib.parse
import configparser
from Crypto.Cipher import AES
import base64


def history_filter(url: str) -> bool:
    """
    It is implied that this method is passed to `filter`.
    Arg:
        uri(str): uri
    Return:
        (bool): Keep given uri in list or not
    """
    # drop trailing '/, clean off white space, make lower, create cli-safe uri
    # with parse.quote, but exclude :/ b/c of http://
    url = re.sub("/$", "", urllib.parse.quote(url.strip(), safe=":/").lower())

    # if it is a m$ office or other doc, skip
    # TODO: Other file extensions
    if re.match(".+(pdf|ppt|pptx|doc|docx|txt|rtf|xls|xlsx|jpg|jepg|png|gif)$", url):
        return False
    if re.match(r"https?://www\.google\.com/search.+", url):
        return False
    return True


def get_key():
    parser = configparser.ConfigParser()
    parser.read("./config.ini")
    key = parser["chipher"]["ENCRYPTION_KEY"]
    return key


def encrypt(text: str):
    key = get_key()
    cipher = AES.new(key.encode("utf8"), AES.MODE_EAX)

    ciphertext = cipher.encrypt(text.encode("utf8"))
    return str(key) + ":" + ciphertext.decode("utf8")


def decrypt(encrypted):
    encrypted_decode = base64.b64decode(encrypted)
    iv = encrypted_decode[:16]  # Determine IV from concatenated data
    cipher_text = encrypted_decode[16:]  # Determine ciphertext from concatenated data
    enc_key = get_key()

    key = base64.b64decode(enc_key)
    aes = AES.new(key, AES.MODE_CBC, iv)  # Use CBC-mode
    decrypted = aes.decrypt(cipher_text)  # Remove Base64 decoding
    return decrypted


def unpadPKCS7(data):
    return data[: -data[-1]]
