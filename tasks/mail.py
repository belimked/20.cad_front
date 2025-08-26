import base64
import imaplib
import poplib
import requests

def get_access_token(client_id, refresh_token):
    data = {
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    ret = requests.post('https://login.live.com/oauth20_token.srf', data=data)

    # 打印响应内容和访问令牌
    print(ret.text)
    print(ret.json()['access_token'])
    return ret.json()['access_token']

# 使用访问令牌生成 OAuth2 认证字符串
def generate_auth_string(user, token):
    auth_string = f"user={user}\1auth=Bearer {token}\1\1"
    return auth_string

pop3_server = 'outlook.office365.com'
pop3_port = 995  # 使用 SSL 的 POP3

def connect_pop3(email, access_token):
    server = poplib.POP3_SSL(pop3_server, pop3_port)
    # 使用 OAuth2 进行身份验证
    auth_string = generate_auth_string(email, access_token)
    encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    server._shortcmd(f'AUTH XOAUTH2')
    server._shortcmd(f'{encoded_auth_string}')

    # 获取邮件列表
    num_messages = len(server.list()[1])
    print(f"收件箱中有 {num_messages} 封邮件。")

    # 获取邮件内容
    for i in range(num_messages):
        response, lines, octets = server.retr(i + 1)
        msg_content = b"\n".join(lines).decode("utf-8")
        print(f"邮件 {i + 1}:")
        print(msg_content)
        print("=" * 50)

def connect_imap(email, access_token):
    mail = imaplib.IMAP4_SSL('outlook.office365.com')
    # 打印生成的认证字符串
    print(generate_auth_string(email, access_token))
    mail.authenticate('XOAUTH2', lambda x: generate_auth_string(email, access_token))
    mail.select("INBOX")
    status, messages = mail.search(None, 'ALL')
    print("邮件 ID:", messages)
    mail.logout()

# 设置电子邮件地址和刷新令牌
client_id = '8b4ba9dd-3ea5-4e5f-86f1-ddba2230dcf2'
email = "MyrticeArmenta36@outlook.com"
t = "M.C540_BL2.0.U.-ChnzihQNmEwonoVcq0vbyUNBw5tcpUcw4oeZMcuEblKbo9z4l013lSb3FLtrXw6wdyKtLuQxVMxhieWkgWhsjBLG!bf2gt2rXonQxsE5c2bHvjsZ563mO!5m2D5TEyhZbNiGMbrhoT7a2m!!CBLDGUWS5DRpsv8BSV4wSEImbTTl4!6eYb*EgrX1ORS!4Fjw!I2IK!4tpHeJcoVFieKVQ*FE*fNbgRdiN084mF20VhGV7LWPDhdq9Vmwo4xvPSZKok7bmkdZSHmffACRYNxpwpmyCNw9FvzqyaLfAJP2oPZ0A2UT*UlVSryf43pMfZB11luZkj9l0DPIEwE5QLDVSESKbYGupbl9wgK84yLDle5dqaGEhe9txLQ3AHbpkkPkKTM8T21q4B49NtQNwVAef9Y$"

# 使用刷新令牌获取访问令牌
acc_token = get_access_token(client_id, t)

# 连接到 IMAP 服务器并访问邮件
connect_imap(email, acc_token)
connect_pop3(email, acc_token)
