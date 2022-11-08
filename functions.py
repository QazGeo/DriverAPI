# bcrypt - hashing, password...
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import africastalking
import bcrypt
import string
import random
from os import urandom
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
import re

def password_hash(password):
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes,salt)
    print("Bytes ", bytes)
    print("Salt ", salt)
    print("Hash ", hash.decode())
    return hash.decode()

# password_hash("nairobi1234")

# $2b$12$GcEMIU8inJS5UMbazI9MUOKgZDK6ubmnF4RFPn4OtpxU8e3smq17q

def password_verify(input_password, hash):
    userBytes = input_password.encode("utf-8")
    result = bcrypt.checkpw(userBytes, hash.encode())
    print("Status", result)
    return result

# password_verify("nairobi1234", "$2b$12$GcEMIU8inJS5UMbazI9MUOKgZDK6ubmnF4RFPn4OtpxU8e3smq17q")

# end password



# for sms

def send_sms(phone, message):
    africastalking.initialize(username = "joe2022", api_key = "aab3047eb9ccfb3973f928d4ebdead9e60beb936b4d2838f7725c9cc165f0c8a")
    sms = africastalking.SMS
    recipient = [phone]
    sender = "AFRICASTKING"
    try:
        response = sms.send(message, recipient)
        print(response)
    except Exception as error:
        print("Exception is", error)

# send_sms("0104342450", "Qaz here, testing...")

# end sms



# start email

def send_email(receiver_address, mail_content, subject):

    # mail_content = "Testing for mwah"
    # The mail addresses and password
    sender_address = 'modcomlearning2@gmail.com'
    sender_pass = '!@#$Mwas@@2'
    # receiver_address = 'receiver567@gmail.com'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

# send_email("modcomlearning@gmail.com", "Testing email", "TestingSYS001")

# randomizer - assignment

def randomizer():

    # initializing size of string
    N = 6

    # using random.choices()
    # generating random strings
    res = ''.join(random.choices(string.ascii_uppercase +
        string.digits, k=N))

    # print result
    print("The generated random string : " + str(res))
    return str(res)

# randomizer()

# encryptions

def encrypters():
    # For Generating cipher text
    secret_key = urandom(16)
    iv = urandom(16)
    obj = AES.new(secret_key, AES.MODE_CBC, iv)

    # Encrypt the message
    message = 'Lorem Ipsum text'
    print('Original message is: ', message)
    encrypted_text = obj.encrypt(message)
    print('The encrypted text', encrypted_text)

def write_key():
    key = Fernet.generate_key()
    with open('key.key', "wb") as key_file:
        key_file.write(key)

# write_key()

def load_key():
    return open("key.key", "rb").read()

# load_key()

def encypt(data):
    key = load_key()
    fernet = Fernet(key)
    encypt_data = fernet.encrypt(data.encode())
    print("No encrypt", data)
    print("Encrypted data", encypt_data.decode())
    return encypt_data

# encypt("0104342450")

# b'gAAAAABjIYbnFiP8PfdjsVSVr-2-tC-gICjYREviWzPDUlcGOkTKYT88h4MALhVsAEtewlA5KEL4ZM6cXF-L0BVE4gkuzwLCuQ=='

def decrypt(data):
    key = load_key()
    fernet = Fernet(key)
    decrypt_data = fernet.decrypt(data)
    print("Decrypted data", decrypt_data.decode())
    return decrypt_data.decode()

# decrypt("gAAAAABjIY4JInrU9a2hOrdMZul8p6L_KgwqAbywpIOpDgv-j3dxWecD9t48y8pD1uErP4uK4OW90ljWj-n338aKTcCGx8QkKA==")

def emailval(s):
   pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,s):
      return True
   return False

# s = "werr@gmail.com"
# print(emailval(s))

def password_check(passwd):
    SpecialSym = ['$', '@', '#', '%']
    val = True

    if len(passwd) < 8:
        return 'length should be at least 6'

    if not any(char.isdigit() for char in passwd):
        return 'Password should have at least one numeral'

    if not any(char.isupper() for char in passwd):
        return 'Password should have at least one uppercase letter'

    if not any(char.islower() for char in passwd):
        return 'Password should have at least one lowercase letter'

    if not any(char in SpecialSym for char in passwd):
        return 'Password should have at least one of the symbols $@#'
    else:
        return True

def phonevalid(phone):
    regex = "^\+254\d{9}"
    if not re.match(regex, phone) or len(phone) != 13:
        return False
    else:
        return True
# print(phonevalid("+254713995445"))



# print(password_check("klguiuyi3A$"))