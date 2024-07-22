from streamlit_authenticator.utilities.hasher import Hasher

passwords = ['123abc','123def','123klm','123adf']

hashed_passwords = Hasher(passwords).generate()

print(hashed_passwords)