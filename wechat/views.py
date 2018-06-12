from django.shortcuts import render, HttpResponse
from django.views import View
import requests
import json

# Create your views here.

class Wechat(View):

    def get(self, request):
      return HttpResponse('GET OK')

    def post(self, request):
        tagList = request.POST.get('tos').split(',')
        content = request.POST.get('content')
        contentList = []
        tmp = ''
        for i in content:
            if i == '[':
                pass
            elif i == ']':
                contentList.append(tmp)
                tmp = ''
            else:
                tmp += i

        print(contentList)


        appid = "wx2d49994aa302d9c4"
        secret = "095ca8370742c08c08e58e879202b32a"
        template_id = "DfTsDSbSUM0wvnXXIjqe7UDNMsVGkM0ZIHTfPXUKi7c"
        accesstoken = self.gettoken(appid, secret)
        subject = '报警状态:   %s' % contentList[1]
        host = contentList[2]
        content = contentList[4].strip().split()[0] + "[" + contentList[4].strip().split()[1] + " " + contentList[4].strip().split()[2] + " " +  contentList[4].strip().split()[3] + "]"
        alertTime = contentList[-1].split()[1] + ' ' + contentList[-1].split()[2]
        tag = '101'

        userList = self.getopenid(accesstoken, tag)
        for user in userList:
            self.senddata(accesstoken, user, template_id, subject, content, host, alertTime)

        return HttpResponse('OK')

    def gettoken(self, appid, secret):
        gettoken_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + secret
        print(gettoken_url)
        try:
            token_file = requests.get(gettoken_url)
        except requests.HTTPError as e:
            print(e.strerror)
            return False
        token_data = token_file.content.decode('utf-8')
        print(token_data)
        token_json = json.loads(token_data)
        token_json.keys()
        token = token_json['access_token']
        return token

    def getopenid(self, access_token, tag_id):
        send_url = "https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token=" + access_token
        send_values = {
            "tagid": tag_id
        }
        send_data = json.dumps(send_values, ensure_ascii=False).encode('utf-8')
        send_request = requests.post(send_url, send_data)
        response = json.loads(send_request.content.decode('utf-8'))
        user_list = response['data']['openid']
        return user_list

    def senddata(self, access_token, user, template_id, subject, content, host, alertTime):
        send_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=" + access_token
        # 发送简单消息
        send_values = {
            "touser": user,
            "template_id": template_id,
            "url": "",
            "topcolor": "#FF0000",
            "data": {
                "first": {
                    "value": subject
                },
                "keyword1": {
                    "value": alertTime
                },
                "keyword2": {
                    "value": host
                },
                "keyword3": {
                    "value": content
                }
            },
        }
        send_data = json.dumps(send_values, ensure_ascii=False).encode('utf-8')
        send_request = requests.post(send_url, send_data)
        response = json.loads(send_request.content.decode('utf-8'))
        print(str(response))
