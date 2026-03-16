"""Ticket number cryptography service."""


class TicketCryptographyService:
    """Service for encrypting and decrypting ticket serial numbers."""
    
    _key = {
        "A": "H", "B": "7", "C": "M", "D": "F", "E": "P", "F": "V",
        "G": "U", "H": "G", "I": "K", "J": "I", "K": "L", "L": "Q",
        "M": "2", "N": "5", "O": "0", "P": "O", "Q": "B", "R": "Y",
        "S": "W", "T": "4", "U": "3", "V": "1", "W": "X", "X": "J",
        "Y": "9", "Z": "A", "0": "D", "1": "6", "2": "N", "3": "R",
        "4": "E", "5": "T", "6": "C", "7": "Z", "8": "S", "9": "8",
    }
    
    _reverse_key: dict[str, str] = {}
    
    def __init__(self):
        self._reverse_key = {v: k for k, v in self._key.items()}
    
    def encrypt(self, text: str) -> str:
        """Encrypt ticket serial number."""
        encrypted_text = ""
        for char in text:
            if char.isalnum():
                encrypted_char = self._key.get(char.upper(), char)
                encrypted_text += encrypted_char
            else:
                encrypted_text += char
        return encrypted_text
    
    def decrypt(self, encrypted_text: str) -> str | None:
        """Decrypt ticket serial number."""
        if not encrypted_text:
            return None
        
        decrypted_text = ""
        for char in encrypted_text:
            if char.isalnum():
                decrypted_char = self._reverse_key.get(char.upper())
                if decrypted_char is None:
                    return None
                decrypted_text += decrypted_char
            else:
                decrypted_text += char
        return decrypted_text
