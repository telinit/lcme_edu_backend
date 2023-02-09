class AES:
    @staticmethod
    def encrypt(key: bytes, plaindata: bytes) -> bytes:
        from Crypto.Cipher import AES

        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plaindata)

        res = b"" + cipher.nonce + tag + ciphertext

        return res

    @staticmethod
    def decrypt(key: bytes, encdata: bytes) -> bytes:
        from Crypto.Cipher import AES

        nonce, tag, ciphertext = encdata[0:16], encdata[16:32], encdata[32:]

        cipher = AES.new(key, AES.MODE_EAX, nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)