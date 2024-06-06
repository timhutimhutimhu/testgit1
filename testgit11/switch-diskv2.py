from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command,netmiko_save_config,netmiko_send_config
from nornir_utils.plugins.tasks.files import write_file
from nornir.core.task import Task,Result
import re,time
import smtplib
from email.mime.text import MIMEText        # 负责构造邮件正文
from email.header import Header

dd = {}
ddd = {}
c = 'cpu_usage:'
mail_host = "smtp.163.com"  # SMTP服务器
mail_user = "timhugw@163.com"  # 用户名
mail_pass = "KHPZJFTDNCKCZPPJ"  # 授权密码，非登录密码
sender = 'timhugw@163.com'  # 发件人邮箱(最好写全, 不然会失败)
receivers = ['12149044@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
# content = c + str(dd) + m + str(ddd)


#加载config，创建一个nornir对象
nr = InitNornir(config_file="config.yaml")
outputs = []
nums=[]

def show_cmds3(task):

    #Task类通过host属性，读取yaml配置，获取其中设备信息
    cmds = task.host['cmds2']
    for cmd in cmds:
        # print(cmd)
        #Task类调用run方法，执行任务，如netmiko_send_command、write_file等插件
        result = task.run(netmiko_send_command, command_string=cmd)
        output = result.result
        write_result=task.run(write_file,
                              filename='server.log',
                              content='\n'+'\n'+'IP:'+f'{task.host.hostname}'+'\n'+output+'\n',
                              append=True)

        print(write_result)
        # sn_table = [hostname,tj]
        # sn_tables.append(sn_table)
def sendEmail(content='disk useing hight'):
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = sender
    message['To'] = ",".join(receivers)
    message['Subject'] = '服务器'
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)
while True:
    total = []
    nu=[]
    fp = open("server.log", "w")
    fp.write('开始统计服务器磁盘空间占用情况,统计时间为：'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    fp.close()
    targets = nr.filter(site='server')
    # targets = nr.filter(site='server')
    results = targets.run(task=show_cmds3)
    print_result(results)

    count=0
    js=[]
    # with open( "server1.log", "r") as fr:
    #     fr.seek(count)  # 根据文件指针进行文件内容读取
    #     for line in fr:  # 循环拿每一行内容
    #         if len(''.join(re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line))) !=0 or ((len(''.join(re.findall(r"[7-9][0-9]+%", line)))!=0 or '100%' in line) and ('iso' not in line)):   #筛选出行中有IP或有百分数的行
    #             print(line)
    #             js.append(line)
    #             with open("diskusagealerm.txt", "a") as mon:
    #                 mon.write(line)
    #     count = fr.tell()  # 读完之后更新文件的指针
    #     fr.close()  # 最后关闭文件句柄
    with open("server.log", "r") as fr:
        fr.seek(count)  # 根据文件指针进行文件内容读取
        for line in fr:  # 循环拿每一行内容

            if len(line) == 1 and nu != []:  # 判断连续行是否结束，结束则连成组
                # print(nu)
                if (len(''.join(re.findall(r"[5-9][0-9]+%", str(nu)))) != 0 or '100%' in str(nu)) and (
                        'iso' not in str(nu)):  # 筛选出行中有IP或有百分数的行
                    # print(re.findall(r"[3-9][0-9]+%", str(nu)))
                    print(str(nu),)
                    print('=============================')
                    sendEmail(str(nu))
                    time.sleep(1)
                    total.append(str(nu))
                    with open("diskusagealerm.txt", "a") as mon:
                        mon.write(str(nu))
                nu = []
            else:
                nu.append(line)

        count = fr.tell()  # 读完之后更新文件的指针
        fr.close()  # 最后关闭文件句柄
    # if len(total) > 1:
    #     sendEmail(str(total))
    time.sleep(300)

