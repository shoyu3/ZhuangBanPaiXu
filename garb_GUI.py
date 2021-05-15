import requests
import json
import time
import os,sys
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import threading
import base64
try:
    from iconwin import img
except:
    pass
def cookie_to_json(cookies_str):
    cookies_dict={}
    for cookie in cookies_str.split(';'):
        cookies_dict[cookie.split('=')[0]]=cookie.split('=')[-1]
    return cookies_dict
def setIcon(win):
    #释放icon.py所保存的图标，打包exe时要用
    tmp=open('tmp.ico','wb+')
    tmp.write(base64.b64decode(img))#写入到临时文件中
    tmp.close()
    win.iconbitmap("tmp.ico") #设置图标
    os.remove("tmp.ico")           #删除临时图标

#2021年5月16日03:09:15

version='1.0'
window = Tk()
window.title('装扮顺序排列 版本'+version+' B站：派蒙月饼')
#window.geometry("400x600")
width=390
heigh=600
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()-50
window.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))
window.resizable(0,0)
try:
    window.iconbitmap('icon.ico')
except:
    try:
        setIcon(window)
    except:
        pass
lbl = Label(window, text="装扮列表")
listbox = Listbox(window,width=45,height=10,relief='solid',borderwidth=1)#,justify='center'
# 向上移动
def list_Up(filter_list):
    a = listbox.get(ANCHOR)  # 获取选择的列表值
    p = filter_list.index(a) - 1  # 获取选择值在列表中的位置
    if p>=0:
        if p == -1:
            listbox.delete(0, END)  # 清空列表框
        elif p != -1:  # 如果位置不等于-1
            filter_list.insert(p, a)  # 列表中插入位置p，值为选择的值
            del filter_list[p + 2]  # 删除掉原位置的值

            listbox.delete(0, END)  # 清空列表框
        for item in filter_list:  # 循环列表
            listbox.insert(END, item)  # 列表框最后插入值
        #tkinter.messagebox.showinfo("","向上移动了一个位置")
        listbox.activate(p)
        listbox.selection_anchor(p)
        listbox.selection_set(p)
        listbox.see(p)
    return filter_list


# 向下移动
def list_Down(filter_list):
    a = listbox.get(ANCHOR)
    p = filter_list.index(a) + 2
    if p<=len(m):
        filter_list.insert(p, a)
        del filter_list[p - 2]
        listbox.delete(0, END)
        for item in filter_list:
            listbox.insert(END, item)
        listbox.activate(p-1)
        listbox.selection_anchor(p-1)
        listbox.selection_set(p-1)
        listbox.see(p-1)
    return filter_list

def ApplyChange():
    lboxlist=listbox.get('0', END)
    garb_id_list=[]
    for i in lboxlist:
        garb_id_list.append(gt_dict[i])
    print(garb_id_list)
    global chkupdwindow,chklbl1
    chkupdwindow = Toplevel(window)
    chkupdwindow.title('保存修改')
    chkupdwindow.configure(bg='white')
    chkupdwindow.transient(window)
    try:
        chkupdwindow.iconbitmap('icon.ico')
    except:
        try:
            setIcon(chkupdwindow)
        except:
            pass
    width = 300
    heigh = 100
    screenwidth = chkupdwindow.winfo_screenwidth()
    screenheight = chkupdwindow.winfo_screenheight()
    chkupdwindow.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))
    chkupdwindow.resizable(0,0)
    chklbl1 = Label(chkupdwindow, text="正在应用排序… (/ω＼*)", justify="center")
    chklbl1.configure(bg='white')
    chklbl1.place(relx = 0.5, rely = 0.4, anchor = "center")
    chkupdthread=threading.Thread(target=do_garb_sort,args=(garb_id_list,))
    chkupdthread.start()
    chkupdwindow.lift()
    chkupdwindow.grab_set()
    chkupdwindow.mainloop()

def do_garb_sort(g_id_list):
    delay=1
    g_id_list=list(reversed(g_id_list))
    print('由于B站后端问题，需额外等待 '+str(delay*len(g_id_list)+1)+' 秒')
    for i in range(len(g_id_list)):
        cookie_dict=cookie_to_json(cookie)
        csrf_token=cookie_dict.get('bili_jct')
        data={
        "csrf":csrf_token,
        "ids":g_id_list[i],
        }
        res = requests.post(url='http://api.bilibili.com/x/garb/user/suit/asset/list/sort',data=data,headers=header)
        message=json.loads(res.text)
        if not message['code'] == 0:
            chkupdwindow.destroy()
            tkinter.messagebox.showwarning('提示','装扮排序保存失败，返回信息为：'+message['message'])
            return False
        chklbl1.configure(text='正在应用修改… (/ω＼*)\n('+str(i+1)+'/'+str(len(g_id_list))+')')
        time.sleep(delay)
    chkupdwindow.destroy()
    tkinter.messagebox.showinfo('提示','装扮排序保存成功！')

def getgarblist():
    global glist,glist_id,gtext,gt_dict
    print('正在获取装扮列表……')
    header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
    "Cookie":cookie,
    }
    r=requests.get('http://api.bilibili.com/x/garb/user/suit/asset/list?is_fans=true&part=suit&pn=1&ps=999&state=active',headers=header).text
    jdata=json.loads(r)['data']
    garblist=jdata['list']
    glist_id=[]
    glist=[]
    gtext=[]
    gt_dict={}
    #print('>>总共有 '+str(jdata['page']['total'])+' 套装扮<<')
    #print('----------------------------------------')
    for i in range(len(garblist)):
        garba=garblist[i]
        now_id=garba['item']['item_id']
        glist_id.append(now_id)
        glist.append((garba['item']['item_id'],garba['fan']['name'],garba['fan']['number'],))
        now_t='NO.'+str(garba['fan']['number']).rjust(6,'0')+' '+garba['fan']['name']+' (ID:'+str(garba['item']['item_id'])+') '+garba['fan']['date']
        gtext.append(now_t)
        gt_dict[now_t]=now_id
        #print(str(i+1)+' '+garba['fan']['name']+'(ID:'+str(garba['item']['item_id'])+') 当前展示：NO.'+str(garba['fan']['number']).rjust(6,'0')+' '+garba['fan']['date'])
        #print(str(i+1)+' NO.'+str(garba['fan']['number']).rjust(6,'0')+' '+garba['fan']['name']+'(ID:'+str(garba['item']['item_id'])+') '+garba['fan']['date'])
    #print('----------------------------------------')
    lbl.configure(text='装扮列表 总数：'+str(len(glist)))

def Refresh():
    global m
    getgarblist()
    listbox.delete('0',END)
    m=gtext
    for x in m:
        listbox.insert(END, x)
    listbox.selection_anchor(0)
    tkinter.messagebox.showinfo('提示','刷新完成！')

try:
    cook=open('cookie.txt','r')
except:
    tkinter.messagebox.showwarning('提示','请先在目录下放入格式正确的cookie.txt！')
    sys.exit()
cookie=cook.read()
print('尝试使用预设的cookie进行模拟登录……')
header={
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
"Cookie":cookie,
}
r=requests.get('http://api.bilibili.com/x/space/myinfo',headers=header).text
userinfo_dict=json.loads(r)
try:
    jdata=userinfo_dict['data']
    myuid=jdata.get('mid')
    name=jdata.get('name')
    level=jdata.get('level')
    coins=jdata.get('coins')
    cookie_dict=cookie_to_json(cookie)
    csrf_token=cookie_dict.get('bili_jct')
    print('模拟登录成功，UID：'+str(myuid)+'，用户名：'+name+'，等级 '+str(level)+'，拥有 '+str(coins)+' 枚硬币')
except:
    tkinter.messagebox.showwarning('提示','模拟登录失败！可能是cookie过期或未登录，请重新获取cookie！')
    sys.exit()

#m = [0,1,2,3,4,5,6,7,8,9,10,11]
getgarblist()
m=gtext
for x in m:
    listbox.insert(END, x)
btn = ttk.Button(window, text="向上移动", command=lambda:list_Up(m))
btn2 = ttk.Button(window, text="向下移动", command=lambda:list_Down(m))
btn4 = ttk.Button(window, text="刷新列表", command=Refresh)
btn3 = ttk.Button(window, text="保存修改", command=ApplyChange)
lbl.pack()
listbox.pack(fill=BOTH, expand=True)
btn.pack()
btn2.pack()
#btn4.pack()
#btn3.pack()
#btn3.place(x=10, y=560)
btn3.place(x=270, y=560)
btn4.place(x=30, y=560)
listbox.selection_anchor(0)
window.mainloop()
