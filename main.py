import uuid
import json
import random
import ssl
import requests

class PayPay:
    
    def __init__(self):
        self.token = ""
        self.uuid = ""
        self.phone = None
        self.password = ""
        self.auth_token = ""
        self.prefix = ""
        self.otp_id = ""
    
    def set_account_infomation(self, phone, password, id = str(uuid.uuid4())):
        self.phone = phone
        self.password = password
        self.uuid = id
        return self.uuid
    
    def login(self, phone = None, password = None, id = None):
        if phone == None:phone = self.phone
        if password == None:password = self.password
        if id == None:id = self.uuid
        json_data = {
            "scope":"SIGN_IN",
            "grant_type":"password",
            "username":str(phone),
            "password":str(password),
            "add_otp_prefix":True,
            "language":"ja-JP",
            "client_uuid": id
        }
        response = requests.post("https://www.paypay.ne.jp/app/v1/oauth/token", json = json_data)
        type = None
        try:
            if response.json()["result_info"]["result_code"] == "SUCCESS":
                self.prefix = response.json()["otp_prefix"]
                self.otp_id = response.json()["otp_reference_id"]
                return True, response.json()["otp_prefix"], response.json()["otp_reference_id"]
            else:
                return False, response.json()["result_info"]["result_msg"]
        except:
            self.auth_token = response.json()["access_token"]
            self.token = str(response.cookies.get("token"))
            return None, response.json()["access_token"], response.cookies.get("token"), id
    
    def get_self(self, link, token = None):
        if token == None:token = self.token
        return requests.get("https://www.paypay.ne.jp/app/v1/users/self?", headers = {"User-Agent":"Mozilla/5.0", "Referer": f"https://www.paypay.ne.jp/app/p2p/{link.replace('https://pay.paypay.ne.jp/', '')}?pid=SMS"}, cookies = {"token": token}).status_code == 200
    
    def login_otp(self, otp, prefix = None, otp_id = None, id = None):
        if id == None:id = self.uuid
        if prefix == None:prefix = self.prefix
        if otp_id == None:otp_id = self.otp_id
        json_data = {
            "scope":"SIGN_IN",
            "grant_type":"otp",
            "otp":str(otp),
            "otp_prefix":prefix,
            "otp_reference_id":otp_id,
            "username_type":"MOBILE",
            "language":"ja-JP",
            "client_uuid": id
        }
        response = requests.post("https://www.paypay.ne.jp/app/v1/oauth/token", json = json_data)
        self.auth_token = response.json()["access_token"]
        self.token = str(response.cookies.get("token"))
        return response.json()["access_token"], response.cookies.get("token"), id
    
    def get_link(self, link, id = None):
        if id == None:id = self.uuid
        link_info = requests.get(f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PLinkInfo?verificationCode={link.replace('https://pay.paypay.ne.jp/', '')}&client_uuid={id}", headers = {"User-Agent":"Mozilla/5.0"}).json()
        if link_info["header"]["resultCode"] == "S0000":
                data = {
                    "requestAt": link_info["payload"]["message"]["data"]["transactionAt"],
                    "orderId": link_info["payload"]["message"]["data"]["orderId"],
                    "verificationCode": link.replace('https://pay.paypay.ne.jp/', ''),
                    "requestId": link_info["payload"]["message"]["data"]["requestId"],
                    "senderMessageId": link_info["payload"]["message"]["messageId"],
                    "senderChannelUrl": link_info["payload"]["message"]["chatRoomId"],
                    "iosMinimumVersion": link_info["payload"]["message"]["iosMinimumVersion"],
                    "androidMinimumVersion": link_info["payload"]["message"]["androidMinimumVersion"],
                    "client_uuid": id
                }
                return link_info["header"]["resultCode"], int(link_info["payload"]["message"]["data"]["amount"]), data, link_info
        else:return link_info["header"]["resultCode"], link_info

    
    def accept_link(self, link, json_data, token = None):
        if token == None:token = self.token
        return requests.post("https://www.paypay.ne.jp/app/v2/p2p-api/acceptP2PSendMoneyLink", json = json_data, cookies = {"token": token}).status_code == requests.codes.ok
    
    def reject_link(self, link, json_data, token = None):
        if token == None:token = self.token
        return requests.post("https://www.paypay.ne.jp/app/v2/p2p-api/rejectP2PSendMoneyLink", json = json_data, cookies = {"token": token}).status_code == requests.codes.ok