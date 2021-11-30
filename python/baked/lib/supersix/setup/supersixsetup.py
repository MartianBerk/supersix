from datetime import datetime

from baked.lib.admin.service.accountservice import AccountService
from baked.lib.admin.service.credentialservice import CredentialService
from baked.lib.admin.service.userservice import UserService

from baked.lib.protected.protected import encrypt, hash_string
from baked.lib.setup.abstractsetup import AbstractSetup
from baked.lib.supersix.model.admin import Account, User, UserData


class SupersixSetup(AbstractSetup):
    """Setup Supersix Backend."""

    def setup(self):
        # encryption key
        cred_service = CredentialService()
        key = cred_service.get_key()
        if not key:
            key = CredentialService().create_key()

        account_service = AccountService("supersix")
        aid = len(account_service.list()) + 1
        admin_account = Account(id=aid, account_id="admin")
        public_account = Account(id=aid + 1, account_id="players")

        for account in [admin_account, public_account]:
            # ensure admin doesn't already exist
            try:
                account_service.get(account_id=account.account_id)

                raise EnvironmentError(f"{account.account_id} already exists.")

            except ValueError:
                account_service.create(account)

        # add root user
        user_service = UserService("supersix")
        uid = len(user_service.list()) + 1

        user_data = UserData(key=key,
                             pwd_hash=encrypt(key, hash_string("admin")),
                             pwd_last_updated=datetime.now())

        user = User(id=uid, account="admin", email="admin@supersix.com", user_id="admin", data=user_data)

        user_service.create(user)

    def get_admin_user_id(self):
        return "user_id", "admin"
