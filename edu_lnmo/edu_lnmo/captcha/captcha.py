import base64
import random
from io import BytesIO

import captcha
import num2words
from captcha.image import ImageCaptcha

from ..util.aes import AES
from ..settings import CAPTCHA_CHALLENGE_KEY, BASE_DIR


class Captcha:

    challenge: str
    challenge_str: str
    solution: str

    def __init__(self, challenge: str = None):
        if challenge is not None:
            enc = base64.b32decode(challenge)
            plain = AES.decrypt(CAPTCHA_CHALLENGE_KEY, enc).decode()
            x, y = tuple(map(int, plain.split(",")))
            self.challenge = challenge
        else:
            x, y = random.randint(0, 100), random.randint(0, 100)
            plain = f"{x},{y}".encode()
            enc = AES.encrypt(CAPTCHA_CHALLENGE_KEY, plain)
            self.challenge = base64.b32encode(enc).decode()
        sx, sy = num2words.num2words(x, lang="ru"), num2words.num2words(y, lang="ru")

        if random.randint(0, 1) == 1 or x < y:
            challenge_str, solution = f"{sx} плюс {sy}", f"{x + y}"
        else:
            challenge_str, solution = f"{sx} минус {sy}", f"{x - y}"

        self.challenge_str = challenge_str
        self.solution = solution

    def generate_image(self) -> bytes:
        buff = BytesIO()
        fonts = [f"{BASE_DIR}/edu_lnmo/assets/PlayfairDisplaySC-Regular.ttf"]
        image = ImageCaptcha(width=500, height=150, fonts=fonts)
        image.generate_image(self.challenge_str).save(buff, format="PNG")

        buff.seek(0)
        return buff.read()

    def test_response(self, response: str) -> bool:
        return str(response).lower() == self.solution.lower()