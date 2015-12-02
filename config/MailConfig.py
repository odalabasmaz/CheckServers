# MailService
mail_server_debug_enabled = True

server_address = "smtp.gmail.com"
server_port = 465

sender_address = ""  # any@any.com
sender_password = ""  # my_secret_pass

receiver_addresses = []  # ["any@any.com", "any2@any.com"]
receiver_addresses_cc = []
receiver_addresses_bcc = []

usual_mail_subject = "PROD SERVER INFORMATION [INFO]"
failure_mail_subject = "PROD SERVER INFORMATION [FAILURE]"

mail_signature = """\
--</br>
Best wishes..</br>
"""
