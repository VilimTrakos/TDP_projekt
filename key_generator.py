from cryptography.fernet import Fernet

def generate_fernet_key():
    return Fernet.generate_key().decode('utf-8')

def main():
    keys = {
        "ENCRYPTION_KEY_SHARED": generate_fernet_key(),
        "ENCRYPTION_KEY_DOCTOR": generate_fernet_key(),
        "ENCRYPTION_KEY_STAFF": generate_fernet_key()
    }

    for key_name, key_value in keys.items():
        print(f'$env:{key_name} = "{key_value}"')

if __name__ == "__main__":
    main()
