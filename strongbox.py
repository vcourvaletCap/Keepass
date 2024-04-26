import hashlib
import os
import json
import base64
from cryptography.fernet import Fernet

class Strongbox:
    def __init__(self, identifier):
        self.identifier = identifier
        self.key = base64.urlsafe_b64encode(hashlib.sha256(identifier.encode()).digest())
        self.fernet = Fernet(self.key)
        self.passwords = {}
    
    def initiate_password(self, sb_password):
        encrypted_sb_password = self.fernet.encrypt(sb_password.encode()).decode()
        self.sb_password = encrypted_sb_password

    def add_password(self, site, password):
        encrypted_password = self.fernet.encrypt(password.encode()).decode()
        self.passwords[site] = encrypted_password

    def get_password(self, site):
        if site in self.passwords:
            encrypted_password = self.passwords[site]
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
            return decrypted_password
        else:
            return None

    def save_strongbox(self, filename):
        if os.path.exists(filename):
            existing_data = self.load_strongbox(filename)
            presence = 0
            for strongbox_data in existing_data:
                if strongbox_data['identifier'] == self.identifier:
                    presence = 1
                    print('Identifier already existing')
                    break
            
            if presence == 0:
                if existing_data is None:
                    existing_data = []
                existing_data.append({
                    "sb_password": self.sb_password,
                    "identifier": self.identifier,
                    "passwords": self.passwords
                })
                data = existing_data
        else:
            data = {
                "sb_password": self.sb_password,
                "identifier": self.identifier, 
                "passwords": self.passwords
            }

        with open(filename, "w") as file:
            json.dump(data, file)

    @classmethod
    def load_strongbox(cls, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            if data is None:
                return []
            elif isinstance(data, dict):
                return [data]
            return data
        except FileNotFoundError:
            return []
    
    def update_password_from_strongbox(self, filename, identifier_request, site_request, password_request):
        with open(filename, "r+") as file:
            data = json.load(file)
            for strongbox_data in data:
                if strongbox_data['identifier'] == identifier_request:
                    for site, encrypted_password in strongbox_data['passwords'].items():
                        if site == site_request:
                            encrypt_password = self.fernet.encrypt(password_request.encode()).decode()
                            strongbox_data['passwords'][site] = encrypt_password
                            file.seek(0)
                            json.dump(data, file)
                            file.truncate()
                            return
                        
    def delete_password_from_strongbox(self, filename, identifier_request, site_request):
        with open(filename, "r+") as file:
            data = json.load(file)
            for strongbox_data in data:
                if strongbox_data['identifier'] == identifier_request:
                    if site_request in strongbox_data['passwords']:
                        del strongbox_data['passwords'][site_request]
                        file.seek(0)
                        json.dump(data, file)
                        file.truncate()
    @classmethod
    def export_strongbox(cls, initial_filename, export_filename, export_identifier):
        data = cls.load_strongbox(initial_filename)
        if data:
            updated_data = []
            exported_data = None
            for strongbox_data in data:
                if strongbox_data["identifier"] == export_identifier:
                    exported_data = strongbox_data
                else:
                    updated_data.append(strongbox_data)
                if exported_data:
                    with open(export_filename, "w") as export_file:
                        json.dump(strongbox_data, export_file)
                    with open(initial_filename, "w") as init_file:
                        json.dump(updated_data, init_file)
    @classmethod
    def import_strongbox(cls, initial_filename, import_filename):
        with open(import_filename, "r") as import_file:
            imported_data = json.load(import_file)
        data = cls.load_strongbox(initial_filename)
        data.append(imported_data)
        with open(initial_filename, "w") as initial_file:
            json.dump(data, initial_file)
        os.remove(import_filename)
