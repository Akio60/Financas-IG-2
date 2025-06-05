import json
from cryptography.fernet import Fernet

# Substitua pela sua chave Fernet real (a mesma usada no sistema)
# Gere uma chave válida com: from cryptography.fernet import Fernet; print(Fernet.generate_key())
FERNET_KEY = b'BlVdTzXqe19XBBpR3-VAZ4kfDtsrYCGUeVMKMWmcBhQ='  # Substitua pela sua chave gerada

# Caminho do arquivo JSON original (texto)
INPUT_FILE = r'C:\Users\Vitor Akio\AppData\Roaming\Financas-IG\users_db.json'
# Caminho do arquivo criptografado de saída (irá sobrescrever o original)
OUTPUT_FILE = r'C:\Users\Vitor Akio\AppData\Roaming\Financas-IG\users_db.json'

def encrypt_data(data: str) -> bytes:
    f = Fernet(FERNET_KEY)
    return f.encrypt(data.encode('utf-8'))

def main():
    # Lê o JSON original
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    # Serializa novamente para garantir formatação
    data = json.dumps(db, ensure_ascii=False, indent=4)
    # Criptografa
    encrypted = encrypt_data(data)
    # Salva como binário
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(encrypted)
    print("Arquivo users_db.json criptografado com sucesso!")

if __name__ == "__main__":
    main()
