#coding=utf-8

from tkinter import *
import time
import tkinter.font as tkFont
import tkinter.messagebox as tkMbox
import linecache
import random
import pymysql
import datetime

map_btn = [[0 for x in range(9)] for x in range(9)]   #按钮
map_btn_mark = [[0 for x in range(9)] for x in range(9)] #按钮选中标记，1为选中
map_btn_select=[[0 for x in range(3)] for x in range(3)]    #选填答案
map_normal=[[0 for x in range(9)] for x in range(9)] #普通模式下的游戏地图
map_level = 0    #游戏等级
map_max_count = 100 #最多关卡
map_finished = 0 #完成关卡
map_model = 0   #游戏模式
map_btn_canvas=[[[0 for x in range(9)]for x in range(9)]for x in range(9)]
# btn_mark_canvas = 0 #标记功能 1为启动
etime = 25
map_hide_btn=[[0 for x in range(9)] for x in range(9)] #隐藏数字，1为隐藏，创建地图后不可变
map_hide_ans=[[2 for x in range(9)] for x in range(9)] #地图填数状态，0为空，1为有,2为不可变
selected_x = 0  #鼠标选中按钮位置
selected_y = 0
msec = 50
            

class normal_page(object):

    def __init__(self,master=None):
        self.root = master              #定义内部变量
        self.root.geometry("900x610+200+100")
        self.create_page()

    def create_page(self):
        global map_finished
        global map_model

        #导航栏
        menu = Menu(self.root)
        self.root.config(menu=menu)

        start = Menu(menu)
        menu.add_cascade(label='start',menu=start)
        start.add_command(label="Load Game",command=self.load_map)
        start.add_separator()
        start.add_command(label="Save Game",command=self.save_map)
        start.add_separator()
        start.add_command(label="Init Game",command=self.init_game_map)  

        model = Menu(menu)
        menu.add_cascade(label='model',menu=model)
        model.add_radiobutton(label="Simple Model",command=lambda i=1:self.map_model(i))
        model.add_separator()
        model.add_radiobutton(label="Medium Model",command=lambda i=2:self.map_model(i))
        model.add_separator()
        model.add_radiobutton(label="Hard Model",command=lambda i=3:self.map_model(i))
        model.add_separator()
        
        #主界面
        self.frame = Frame(self.root,width=900,height=610)
        self.frame.place(x=0,y=0)
        ft1=tkFont.Font(family='Fixdsys', size=30, weight=tkFont.BOLD)
        self.score_label = Label(self.frame,
            text="",
            anchor=CENTER,
            font=ft1,
            bg="white")
        self.score_label.place(width=610,height=50)

        self.show_process()

        self.process_label = Label(self.frame,
            text="%s/%s"%(map_finished,map_max_count),
            anchor=CENTER,
            font=ft1,
            bg="white",
            fg="#58ACFA")
        self.process_label.place(x=610,y=0,width=240,height=50)        

        self.canvas = Canvas(self.frame,width=900,height=550)
        self.canvas.place(x=0,y=50)

        global map_btn
        global map_hide_btn

        ft2=tkFont.Font(family='Fixdsys', size=30, weight=tkFont.NORMAL)
        for i in range(9):
            for j in range(9):
                map_btn[i][j]=Button(
                    self.frame,
                    text='',                    
                    font=ft2,
                    highlightbackground="#E6E6E6",
                    command=lambda i1=i,j1=j: self.cell_clicked(i1,j1))                    
                map_btn[i][j].place(x=8+i*60,y=3+j*60+55,width=58,height=58)
                # if map_hide_btn[i][j] == 0: #0显示  
                # if map_btn[i][j]['text']==0:
                #     map_btn[i][j].confi           
 
        for i in range(3):
            for j in range(3):
                map_btn_select[i][j]=Button(
                    self.frame,
                    text=i+1+j*3,
                    highlightbackground='#E6E6E6',
                    fg='black',
                    font=ft2,
                    command=lambda i1=i,j1=j: self.put_clicked(i1,j1))
                map_btn_select[i][j].place(x=610+i*80,y=j*80+150,width=80,height=80)

        self.canvas.create_line(5,3,5,550,fill="#000000",width=3)
        self.canvas.create_line(5,5,550,5,fill="#000000",width=3)
        self.canvas.create_line(548,5,548,550,fill="#000000",width=3)
        self.canvas.create_line(5,548,550,548,fill="#000000",width=3)
        self.canvas.create_line(187,5,187,548,fill="#000000",width=3)
        self.canvas.create_line(366,5,366,548,fill="#000000",width=3)
        self.canvas.create_line(5,186,548,186,fill="#000000",width=3)
        self.canvas.create_line(5,366,548,366,fill="#000000",width=3)

        self.new_btn = Button(self.frame,
            text="""New Game""",
            highlightbackground="#58ACFA",
            fg='black',
            font=ft2,
            command=self.create_map
            )
        self.new_btn.place(x=610,y=50,width=240,height=100)
        
        self.delete_btn = Button(self.frame,
            text="""❌\nDelete""",
            highlightbackground='#E6E6E6',
            fg='black',
            font=ft2,
            command=self.delete_clicked)
        self.delete_btn.place(x=610,y=390,width=120,height=100)

        self.suggest_btn = Button(self.frame,
            text="""❓\nHint""",
            highlightbackground='#E6E6E6',
            fg='black',
            font=ft2,
            command=self.hint_given)
        self.suggest_btn.place(x=730,y=390,width=120,height=100)

        self.finish_btn = Button(self.frame,
            text="""❗️\nFinish""",
            font=ft2,
            highlightbackground='#E6E6E6',
            fg='black',
            command=self.win)
        self.finish_btn.place(x=610,y=490,width=120,height=100)           

        self.var = IntVar()  #单选的值
        self.var.set(0)  #initial
        ft3=tkFont.Font(family='Fixdsys', size=20, weight=tkFont.NORMAL)
        self.mark_on=Radiobutton(self.frame,
            text="Mark On",
            font=ft3,
            variable=self.var,
            value=1)
        self.mark_on.place(x=730,y=510,width=120,height=20)

        self.mark_off=Radiobutton(self.frame,
            text="Mark Off",
            font=ft3,
            variable=self.var,
            value=0)
        self.mark_off.place(x=730,y=540,width=120,height=20)  

        self.next_btn = Button(self.frame,
            text="Next",
            highlightbackground='#E6E6E6',
            fg='black',
            font=ft2,
            command=self.next_level)
                   
    def map_model(self,level):
        global map_model

        if level==1:
            map_model=1
            self.score_label.config(text='Simple Model')
        if level==2:
            map_model=2
            self.score_label.config(text='Medium Model')
        if level==3:
            map_model=3
            self.score_label.config(text='Hard Model')

    def show_process(self):
        global map_model
        global map_finished

        db = pymysql.connect('localhost','root','yangwenlong123','Sudoku')
        #cursor方法创建游标对象
        cursor = db.cursor()
        sql1="""
            SELECT COUNT(*)
            FROM game_map
            WHERE tag=1
            """
        sql2="""
            SELECT COUNT(*)
            FROM medium_map
            WHERE tag=1
            """
        sql3="""
            SELECT COUNT(*)
            FROM hard_map
            WHERE tag=1
            """
        #execute执行
        try:
            if map_model==1:
                cursor.execute(sql1)
            if map_model==2:
                cursor.execute(sql2)
            if map_model==3:
                cursor.execute(sql3)

            result=[]
            result=cursor.fetchone()
            map_finished=result[0]
            #提交到数据库执行
            db.commit()
        except:
            db.rollback()
        #关闭数据库
        cursor.close()
        db.close()

    def init_game_map(self):
        global map_max_count
        global map_model

        if map_model==0:
            self.score_label.config(text='Select Map Model')
            return

        #打开数据库连接
        db = pymysql.connect('localhost','root','yangwenlong123','Sudoku')
        #cursor方法创建游标对象
        cursor = db.cursor()
        sql1="""
            SELECT COUNT(*)
            FROM game_map
            """ 
        sql2="""
            SELECT COUNT(*)
            FROM medium_map
            """ 
        sql3="""
            SELECT COUNT(*)
            FROM hard_map
            """ 
        #execute执行
        try:
            if map_model==1:
                cursor.execute(sql1)
            if map_model==2:
                cursor.execute(sql2)
            if map_model==3:
                cursor.execute(sql3)

            result=[]
            result=cursor.fetchone()
            count=result[0]
            #提交到数据库执行
            db.commit()
        except:
            db.rollback()
        #关闭数据库
        cursor.close()
        db.close()

        if count==map_max_count:
            self.score_label.config(text='Game Map Has Been Max')
            return

        while count<map_max_count:
            self.init_map()
            count+=1

        if count==map_max_count:
            self.score_label.config(text='Init Success')

    def init_map(self):

        global map_model

        candidate = [x for x in range(1,10)]
        map_seq = []
        temp=[]
        temp_str=''

        for i in range(9):
            map_seq.append(random.choice(candidate))
            candidate.remove(map_seq[i])

        map_base5=[]
        for i in range(3):
            start = i*3
            end = (i+1)*3
            map_base5.append(map_seq[start:end])

        map_base4=[]
        map_base4.append(map_base5[1])
        map_base4.append(map_base5[2])
        map_base4.append(map_base5[0])

        map_base6=[]
        map_base6.append(map_base5[2])
        map_base6.append(map_base5[0])
        map_base6.append(map_base5[1])

        map_base2=[[0 for x in range(3)]for y in range(3)]
        map_base8=[[0 for x in range(3)]for y in range(3)]
        for i in range(3):
            map_base8[i][2]=map_base2[i][0]=map_base5[i][1]
            map_base8[i][0]=map_base2[i][1]=map_base5[i][2]
            map_base8[i][1]=map_base2[i][2]=map_base5[i][0]

        map_base1=[[0 for x in range(3)]for y in range(3)]
        map_base7=[[0 for x in range(3)]for y in range(3)]
        for i in range(3):
            map_base1[i][1]=map_base7[i][2]=map_base4[i][0]
            map_base1[i][2]=map_base7[i][0]=map_base4[i][1]
            map_base1[i][0]=map_base7[i][1]=map_base4[i][2]
            
        map_base3=[[0 for x in range(3)]for y in range(3)]
        map_base9=[[0 for x in range(3)]for y in range(3)]
        for i in range(3):
            map_base3[i][1]=map_base9[i][2]=map_base6[i][0]
            map_base3[i][2]=map_base9[i][0]=map_base6[i][1]
            map_base3[i][0]=map_base9[i][1]=map_base6[i][2]
            
        for i in range(3):
            for j in range(3):
                temp.append(map_base1[i][j])
            for j in range(3):
                temp.append(map_base2[i][j])
            for j in range(3):
                temp.append(map_base3[i][j])
        for i in range(3):
            for j in range(3):
                temp.append(map_base4[i][j])
            for j in range(3):
                temp.append(map_base5[i][j])
            for j in range(3):
                temp.append(map_base6[i][j])
        for i in range(3):
            for j in range(3):
                temp.append(map_base7[i][j])
            for j in range(3):
                temp.append(map_base8[i][j])
            for j in range(3):
                temp.append(map_base9[i][j])

        #map_num
        a=[]
        for i in temp:
            a.append(str(i))
        temp_str=''.join(a)

        #map_hide_btn and map_hide_ans
        map_num=0
        map_hide=[]
        
        if map_model==1:
            map_num = random.randint(3,4)
        if map_model==2:
            map_num = random.randint(4,5)
        if map_model==3:
            map_num = random.randint(5,6)

        map_hide_btn=[[0 for x in range(9)] for x in range(9)] #隐藏数字，1为隐藏，创建地图后不可变
        map_hide_ans=[[2 for x in range(9)] for x in range(9)] #地图填数状态，0为空，1为有,2为不可变
        for i in range(9):
            map_hide=random.sample(range(1,10),map_num)
            for j in range(map_num):
                map_hide_btn[i][map_hide[j]-1]=1
                map_hide_ans[i][map_hide[j]-1]=0

        a=[]
        b=[]
        for i in range(9):
            for j in range(9):
                a.append(str(map_hide_btn[i][j]))
                b.append(str(map_hide_ans[i][j]))

        map_hide_btn_str=''.join(a)
        map_hide_ans_str=''.join(b)

        #打开数据库连接
        db = pymysql.connect('localhost','root','yangwenlong123','Sudoku')
        #cursor方法创建游标对象
        cursor = db.cursor()
        #sql
        sql1="""
            INSERT INTO game_map(map_num,hide_btn,store_num,hide_ans,tag)
            SELECT '%s','%s','%s','%s',0
            FROM DUAL
            WHERE NOT EXISTS
            (SELECT* FROM game_map WHERE game_map.map_num='%s' AND game_map.hide_btn='%s')
            """%(temp_str,map_hide_btn_str,temp_str,map_hide_ans_str,temp_str,map_hide_btn_str)

        sql2="""
            INSERT INTO medium_map(map_num,hide_btn,store_num,hide_ans,tag)
            SELECT '%s','%s','%s','%s',0
            FROM DUAL
            WHERE NOT EXISTS
            (SELECT* FROM medium_map WHERE medium_map.map_num='%s' AND medium_map.hide_btn='%s')
            """%(temp_str,map_hide_btn_str,temp_str,map_hide_ans_str,temp_str,map_hide_btn_str)
        
        sql3="""
            INSERT INTO hard_map(map_num,hide_btn,store_num,hide_ans,tag)
            SELECT '%s','%s','%s','%s',0
            FROM DUAL
            WHERE NOT EXISTS
            (SELECT* FROM hard_map WHERE hard_map.map_num='%s' AND hard_map.hide_btn='%s')
            """%(temp_str,map_hide_btn_str,temp_str,map_hide_ans_str,temp_str,map_hide_btn_str)
        #execute执行
        try:
            if map_model==1:
                cursor.execute(sql1)
            if map_model==2:
                cursor.execute(sql2)
            if map_model==3:
                cursor.execute(sql3)
            db.commit()
            # tkMbox.showinfo("Notice","Create Success")          
        except:
            db.rollback()  
        #关闭数据库
        cursor.close()
        db.close()

    def create_map(self):
        
        global map_normal
        global map_level
        global map_max_count
        global map_finished
        global map_model
        global map_count_level
        global map_hide_btn
        global map_hide_ans
        global map_btn

        map_normal=[[0 for x in range(9)] for x in range(9)] #普通模式下的游戏地图
        map_hide_btn=[[0 for x in range(9)] for x in range(9)] #隐藏数字，1为隐藏，创建地图后不可变
        map_hide_ans=[[2 for x in range(9)] for x in range(9)] #地图填数状态，0为空，1为有,2为不可变
        for i in range(9):
            for j in range(9):
                map_btn[i][j].config(text='',fg='black',highlightbackground='#E6E6E6')
                map_btn[i][j].config(state="normal")
                    
                # map_btn[i][j].config(highlightbackground="#E6E6E6")

        self.score_label.config(text="")  
        if map_model==0:
            self.score_label.config(text='Select Map Model')
        self.show_process()

        self.process_label.config(text="%s/%s"%(map_finished,map_max_count))              

        candidate = [x for x in range(1,10)]
        map_seq = []
        temp1=[]
        temp2=[]

        #打开数据库连接
        db = pymysql.connect('localhost','root','yangwenlong123','Sudoku')
        #cursor方法创建游标对象
        cursor = db.cursor()
        #sql
        sql1="SELECT ID FROM game_map WHERE tag!=1"
        sql2="SELECT ID FROM medium_map WHERE tag!=1"
        sql3="SELECT ID FROM hard_map WHERE tag!=1"

        if map_model==1:
            cursor.execute(sql1)
        if map_model==2:
            cursor.execute(sql2)
        if map_model==3:
            cursor.execute(sql3)

        result=cursor.fetchall()
        choice=[]
        for i in result:
            choice.append(i[0])

        if len(choice)==0:
            self.score_label.config(text="No Available Map")
        else:
            map_level=random.choice(choice)


        sql1='SELECT map_num,hide_btn FROM game_map WHERE ID=%s AND tag!=1' %(map_level)
        sql2='SELECT map_num,hide_btn FROM medium_map WHERE ID=%s AND tag!=1' %(map_level)
        sql3='SELECT map_num,hide_btn FROM hard_map WHERE ID=%s AND tag!=1' %(map_level)

        #execute执行
        try:
            if map_model==1:
                cursor.execute(sql1)
            if map_model==2:
                cursor.execute(sql2)
            if map_model==3:
                cursor.execute(sql3)

            #获取结果
            result=cursor.fetchall()
            #数据操作
            for i in result:
                result_num = list(i[0])
                result_hide_btn = list(i[1])
            for i in result_num:
                temp1.append(int(i))
            for i in result_hide_btn:
                temp2.append(int(i))
        except:
            db.rollback()

        #关闭数据库
        cursor.close()
        db.close()

        map_num = 0
        map_normal = []

        #普通模式
        # if map_model == 1:
        # if map_level==1:
        # map_num = random.randint(3,4)
        # elif map_level==2:
            # map_num = random.randint(4,5)
        #挑战模式
        # elif map_model == 2:
        #     if map_count_level <6:
        #         map_num = map_count_level
        #         map_count_level+=1
        #     else:
        #         map_count_level=6
        #         map_num = map_count_level

        for i in range(9):
            start = i*9
            end = (i+1)*9
            map_normal.append(temp1[start:end]) 

        for i in range(9):
            for j in range(9):
                map_hide_btn[i][j]=temp2[i*9+j]
                if map_hide_btn[i][j]==1:
                    map_hide_ans[i][j]=0

        

        # map_hide = []
        # for i in range(9):  #隐藏
        #     map_hide = random.sample(range(1,10),map_num)
        #     for j in range(map_num):
        #         map_hide_btn[i][map_hide[j]-1] = 1
        #         map_hide_ans[i][map_hide[j]-1] = 0

        for i in range(9):
            for j in range(9):
                if map_hide_btn[i][j] == 0: #0显示
                    map_btn[i][j].config(text=map_normal[i][j])        
 

        # map_hide_btn[0][0]=1
        # map_hide_btn[1][2]=1
        # map_hide_ans[0][0]=0
        # map_hide_ans[1][2]=0

    def save_map(self):
        global map_normal
        global map_level
        global map_model
        global map_count_level
        global map_hide_btn
        global map_hide_ans
        global map_btn
        global map_btn_canvas

        if map_model==0:
            self.score_label.config(text='Select Map Model')
            return

        temp1=[]
        temp2=[]
        temp3=[]
        temp_num_str=''
        temp_ans_str=''
        temp_map_nor=''
        for i in range(9):
            for j in range(9):
                temp2.append(str(map_hide_ans[i][j]))
                temp3.append(str(map_normal[i][j]))
                if map_btn[i][j]['text']=='':
                    temp1.append(str(0))
                else:
                    temp1.append(str(map_btn[i][j]['text']))
                        

        temp_num_str=''.join(temp1)
        temp_ans_str=''.join(temp2)
        temp_map_nor=''.join(temp3)

        #打开数据库连接
        db = pymysql.connect('localhost','root','yangwenlong123','Sudoku')
        #cursor方法创建游标对象
        cursor = db.cursor()
        #sql
        sql="""
            SELECT count(*)
            FROM game_store
            WHERE model=%s
            """%(map_model)
        sql1="""
            INSERT INTO game_store(store_num,hide_ans,map_num,model)
            VALUES('%s','%s','%s',%s)
            """ %(temp_num_str,temp_ans_str,temp_map_nor,map_model)
        sql2="""
            UPDATE game_store 
            SET store_num='%s',hide_ans='%s',map_num='%s'
            WHERE model=%s
            """%(temp_num_str,temp_ans_str,temp_map_nor,map_model)
        #execute执行
        try:
            cursor.execute(sql)
            result=[]
            result=cursor.fetchone()
            count=result[0]
            if count==0:
                cursor.execute(sql1)
            else:
                cursor.execute(sql2)
            #提交到数据库执行
            db.commit()
            self.score_label.config(text='Save Success')
        except:
            db.rollback()
        #关闭数据库
        cursor.close()
        db.close()

    def load_map(self):
        global map_normal
        global map_level
        global map_model
        global map_count_level
        global map_hide_btn
        global map_hide_ans
        global map_btn

        if map_model==0:
            self.score_label.config(text='Select Map Model')
            return

        map_normal=[[0 for x in range(9)] for x in range(9)] #普通模式下的游戏地图
        map_hide_btn=[[0 for x in range(9)] for x in range(9)] #隐藏数字，1为隐藏，创建地图后不可变
        map_hide_ans=[[2 for x in range(9)] for x in range(9)] #地图填数状态，0为空，1为有,2为不可变
        for i in range(9):
            for j in range(9):
                map_btn[i][j].config(text='',highlightbackground='#E6E6E6')

        self.score_label.config(text="")  
        self.show_process()
        self.process_label.config(text="%s/%s"%(map_finished,map_max_count))              

        temp1=[]
        temp2=[]
        temp3=[]
        db=pymysql.connect('localhost','root','yangwenlong123','Sudoku')
        cursor = db.cursor()

        sql="SELECT store_num,hide_ans,ID,map_num FROM game_store WHERE model=%s"%map_model
        try:
            cursor.execute(sql)
            result=cursor.fetchall()

            for i in result:
                result_num =list(i[0])
                result_hide_ans=list(i[1])
                result_lel=i[2]
                map_res=list(i[3])
            for i in result_num:
                temp1.append(int(i))
            for i in result_hide_ans:
                temp2.append(int(i))
            map_level = result_lel
            for i in map_res:
                temp3.append(int(i))

        except:
            db.rollback()

        cursor.close()
        db.close()

        map_text=[]
        map_ans=[]
        map_n=[]
        for i in range(9):
            start = i*9
            end = (i+1)*9
            map_text.append(temp1[start:end])
            map_ans.append(temp2[start:end])
            map_n.append(temp3[start:end])

        for i in range(9):
            for j in range(9):
                map_normal[i][j]=map_n[i][j]
                if map_text[i][j] == 0:
                    pass
                else:
                    map_btn[i][j].config(text=map_text[i][j])
                map_hide_ans[i][j]=map_ans[i][j] 
                if map_hide_ans[i][j]==2:
                    map_hide_btn[i][j]=0
                else:
                    map_hide_btn[i][j]=1
                if map_ans[i][j] == 1:
                    map_btn[i][j].config(fg='RoyalBlue')              

    def cell_clicked(self,x,y):
        global map_btn
        global map_btn_mark
        global map_hide_ans
        global selected_x
        global selected_y

        self.score_label.config(text='')

        for i in range(9):
            for j in range(9):
                # if  map_btn_mark[i][j] == 1:
                map_btn[i][j].config(highlightbackground='#E6E6E6')
                map_btn[i][j].config(fg='black')
                if map_hide_btn[i][j] == 1 and map_hide_ans[i][j]==1:
                    map_btn[i][j].config(fg='RoyalBlue')  
                    # map_btn_mark[i][j] = 0   

        temp = 0      
        if map_hide_ans[x][y] != 0:  
            temp = map_btn[x][y]['text']
            for i in range(9):
                for j in range(9):
                    if map_btn[i][j]['text'] == temp:                    
                        map_btn[i][j].config(highlightbackground='#81BEF7')
                        # if map_hide_btn[i][j] == 0:
                        # map_btn[i][j].config(fg='GOLD')

        if map_hide_ans[x][y] == 0:
            for i in range(9):
                map_btn[x][i]["highlightbackground"]='#A9D0F5'
                # map_btn[x][i]["fg"]='orange'                
                map_btn[i][y]["highlightbackground"]='#A9D0F5'
                # map_btn[i][y]["fg"]='orange'

        map_btn[x][y].config(highlightbackground='#0080FF')
        # map_btn[x][y].config(fg='red')
        map_btn_mark[x][y] = 1

        selected_x = x
        selected_y = y

    def put_clicked(self,x,y):
        global map_btn
        global map_btn_mark
        global map_btn_select
        global map_hide_btn
        global map_hide_ans
        global selected_x
        global selected_y
        global map_btn_canvas

        for i in range(9):
            if map_btn[selected_x][selected_y]['text'] != map_btn[selected_x][i]['text'] and i!=selected_y:
                map_btn[selected_x][selected_y].config(highlightbackground='#58ACFA')
                map_btn[selected_x][selected_y].config(fg='RoyalBlue')
            if map_btn[selected_x][selected_y]['text'] != map_btn[i][selected_y]['text'] and i!=selected_x:
                map_btn[selected_x][selected_y].config(highlightbackground='#58ACFA')
                map_btn[selected_x][selected_y].config(fg='RoyalBlue')

        if map_hide_btn[selected_x][selected_y] != 0:
            if map_btn_mark[selected_x][selected_y] != 0:
                if self.var.get()==1:
                    ft3=tkFont.Font(family='Fixdsys',size=8,weight=tkFont.NORMAL)
                    cand=[x+1 for x in range(9)]
                    for k in range(9):
                        if map_btn_canvas[selected_x][selected_y][k]==0:
                            map_btn_canvas[selected_x][selected_y][k]=''
                    mark_str="""
                        %s      %s      %s\n
                        %s      %s      %s\n
                        %s      %s      %s
                            """%(map_btn_canvas[selected_x][selected_y][0],map_btn_canvas[selected_x][selected_y][1],
                            map_btn_canvas[selected_x][selected_y][2],map_btn_canvas[selected_x][selected_y][3],
                            map_btn_canvas[selected_x][selected_y][4],map_btn_canvas[selected_x][selected_y][5],
                            map_btn_canvas[selected_x][selected_y][6],map_btn_canvas[selected_x][selected_y][7],
                            map_btn_canvas[selected_x][selected_y][8]) 
                    map_btn[selected_x][selected_y].config(font=ft3,anchor='e',text=mark_str,highlightbackground='#0080FF')

                    for i in cand:
                        if map_btn_select[x][y]['text']==i:
                            map_btn_canvas[selected_x][selected_y][i-1]=i
                    mark_str="""
                        %s      %s      %s\n
                        %s      %s      %s\n
                        %s      %s      %s
                            """%(map_btn_canvas[selected_x][selected_y][0],map_btn_canvas[selected_x][selected_y][1],
                            map_btn_canvas[selected_x][selected_y][2],map_btn_canvas[selected_x][selected_y][3],
                            map_btn_canvas[selected_x][selected_y][4],map_btn_canvas[selected_x][selected_y][5],
                            map_btn_canvas[selected_x][selected_y][6],map_btn_canvas[selected_x][selected_y][7],
                            map_btn_canvas[selected_x][selected_y][8]) 
                    map_btn[selected_x][selected_y].config(font=ft3,anchor='e',text=mark_str,highlightbackground='#0080FF')
                if self.var.get()==0:
                    ft2=tkFont.Font(family='Fixdsys', size=30, weight=tkFont.NORMAL)
                    map_btn[selected_x][selected_y].config(text=map_btn_select[x][y]['text'],                 
                        font=ft2,
                        anchor=CENTER)
                    map_hide_ans[selected_x][selected_y]=1

        for i in range(9):
            if map_btn[selected_x][selected_y]['text'] == map_btn[selected_x][i]['text'] and i!=selected_y:
                map_btn[selected_x][selected_y].config(highlightbackground='red')
            if map_btn[selected_x][selected_y]['text'] == map_btn[i][selected_y]['text'] and i!=selected_x:
                map_btn[selected_x][selected_y].config(highlightbackground='red')

    def delete_clicked(self):
        global map_btn
        global map_btn_mark
        global map_hide_ans
        global map_hide_btn
        global selected_x
        global selected_y
        global map_btn_canvas
    
        ft2=tkFont.Font(family='Fixdsys', size=30, weight=tkFont.NORMAL)
        ft3=tkFont.Font(family='Fixdsys',size=8,weight=tkFont.NORMAL)

        if map_hide_btn[selected_x][selected_y] == 1:
            if map_btn_mark[selected_x][selected_y] == 1:
                if self.var.get()==0:
                    map_btn[selected_x][selected_y].config(text='',font=ft2,
                        anchor=CENTER)  
                    map_hide_ans[selected_x][selected_y]=0
                if self.var.get()==1:
                    for k in range(9):                    
                        map_btn_canvas[selected_x][selected_y][k]=''
                    mark_str="""
                        %s      %s      %s\n
                        %s      %s      %s\n
                        %s      %s      %s
                            """%(map_btn_canvas[selected_x][selected_y][0],map_btn_canvas[selected_x][selected_y][1],
                            map_btn_canvas[selected_x][selected_y][2],map_btn_canvas[selected_x][selected_y][3],
                            map_btn_canvas[selected_x][selected_y][4],map_btn_canvas[selected_x][selected_y][5],
                            map_btn_canvas[selected_x][selected_y][6],map_btn_canvas[selected_x][selected_y][7],
                            map_btn_canvas[selected_x][selected_y][8]) 
                    map_btn[selected_x][selected_y].config(font=ft3,anchor='e',text=mark_str,highlightbackground='#0080FF')

        map_btn[selected_x][selected_y].config(highlightbackground='#0080FF')        

    def next_level(self):
        self.next_btn.place_forget()
        self.create_map()

    def hint_given(self):
        global map_btn
        global map_hide_ans
        global map_normal
        global map_hide_btn
        global selected_x
        global selected_y

        x=selected_x
        y=selected_y

        if map_hide_btn[x][y]==1 and map_hide_ans[x][y]==0:
            map_btn[x][y].config(text=map_normal[x][y],fg='RoyalBlue')
            map_hide_ans[x][y]=1
                        
    def win(self):
        global map_btn
        global map_normal
        global map_level
        global map_finished
        global map_model

        flag=[]

        for i in range(9):
            for j in range(9):
                if map_hide_btn[i][j] == 1:
                    if map_btn[i][j]['text'] == map_normal[i][j]:
                        flag.append(1)                        
                    else:
                        flag.append(0)

        # if flag.__contains__(0):
        result = self.rule()
        if result==243:
            self.score_label.config(text="Win")

            #打开数据库连接
            db = pymysql.connect('localhost','root','yangwenlong123','Sudoku')
            #cursor方法创建游标对象
            cursor = db.cursor()
            sql1="""
                UPDATE game_map SET tag=1
                WHERE ID=%s
                """ %(map_level)
            sql11="""
                SELECT COUNT(*)
                FROM game_map
                WHERE tag=1
                """
            sql2="""
                UPDATE medium_map SET tag=1
                WHERE ID=%s
                """ %(map_level)
            sql22="""
                SELECT COUNT(*)
                FROM medium_map
                WHERE tag=1
                """
            sql3="""
                UPDATE hard_map SET tag=1
                WHERE ID=%s
                """ %(map_level)
            sql33="""
                SELECT COUNT(*)
                FROM hard_map
                WHERE tag=1
                """
            #execute执行
            try:
                if map_model==1:
                    cursor.execute(sql1)
                    cursor.execute(sql11)                    
                if map_model==2:
                    cursor.execute(sql2)
                    cursor.execute(sql22)                
                if map_model==3:
                    cursor.execute(sql3)
                    cursor.execute(sql33)
                    
                result=[]
                result=cursor.fetchone()
                map_finished=result[0]
                #提交到数据库执行
                db.commit()
            except:
                db.rollback()
            #关闭数据库
            cursor.close()
            db.close()

            self.process_label.config(text="%s/%s"%(map_finished,map_max_count))              

            self.next_btn.place(x=610,y=490,width=120,height=100)
            for i in range(9):
                for j in range(9):
                    map_btn[i][j].config(state="disabled")
                    map_btn[i][j].config(highlightbackground="#E6E6E6")
        else:
            self.score_label.config(text="Fall")
        # else:
        #     self.score_label.config(text="Win")
        #     self.next_btn.place(x=720,y=380,width=150,height=58)
        #     for i in range(9):
        #         for j in range(9):
        #             map_btn[i][j].config(state="disabled")
        #             map_btn[i][j].config(highlightbackground="white")

    def rule(self):
        """
        规则判断胜负
        """
        global map_btn
        global map_normal

        flag=0 #true

        #行列
        row_num=[]
        col_num=[]
        for i in range(9):
            for j in range(9):
                row_num.append(map_btn[i][j]['text'])
                col_num.append(map_btn[j][i]['text'])

        for i in range(9):  
            for j in range(9):          
                if row_num[i*9:(i+1)*9].count(map_btn[i][j]['text']) == 1:
                    flag+=1                
                if col_num[i*9:(i+1)*9].count(map_btn[j][i]['text']) == 1:
                    flag+=1

        #小矩阵
        # candidate = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for i in range(9):
            candidate = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for j in range(9):
                grid_x = i//3*3
                grid_y = j//3*3                   
                if map_btn[grid_x+i%3][grid_y+j%3]['text'] in candidate:
                    candidate.remove(map_btn[grid_x+i%3][grid_y+j%3]['text'])
                    flag+=1

        return flag
        


        

# class challenge_page(normal_page):

#     def create_page(self):
#         global map_count_level
#         global etime
#         if map_count_level >= 6:
#             self.rtime = etime*9*map_count_level
#             etime-=1
#         else:
#             self.rtime = etime*9*map_count_level            

#         self.frame = Frame(self.root,width=900,height=610)
#         self.frame.place(x=0,y=0)
#         ft1=tkFont.Font(family='Fixdsys', size=30, weight=tkFont.BOLD)
        
#         self.remaintime=0.0
#         self.time = StringVar()
#         self.time_label = Label(self.frame,
#             textvariable=self.time,
#             # anchor=CENTER,
#             font=ft1,
#             bg="white",
#             fg='black')
#         self._setTime(self.remaintime)
#         self.time_label.place(width=900,height=50)

#         self.canvas = Canvas(self.frame,width=900,height=550)
#         self.canvas.place(x=0,y=50)

#         global map_btn
#         global map_hide_btn

#         ft2=tkFont.Font(family='Fixdsys', size=30, weight=tkFont.NORMAL)
        
#         self.create_map()

#         for i in range(9):
#             for j in range(9):
#                 map_btn[i][j]=Button(
#                     self.frame,
#                     bg="white",
#                     text='',                    
#                     font=ft2,
#                     command=lambda i1=i,j1=j: self.cell_clicked(i1,j1))                    
#                 map_btn[i][j].place(x=8+i*60,y=3+j*60+55,width=58,height=58)
#                 if map_hide_btn[i][j] == 0: #0显示
#                     map_btn[i][j].config(text=map_normal[i][j])        
 
#         for i in range(3):
#             for j in range(3):
#                 map_btn_select[i][j]=Button(
#                     self.frame,
#                     text=j*3+i+1,
#                     bg='white',
#                     fg='black',
#                     font=ft2,
#                     command=lambda i1=i,j1=j: self.put_clicked(i1,j1))
#                 map_btn_select[i].place(x=610,y=3+i*60+55,width=58,height=58)

#         self.canvas.create_line(5,3,5,550,fill="#000000",width=3)
#         self.canvas.create_line(5,5,550,5,fill="#000000",width=3)
#         self.canvas.create_line(548,5,548,550,fill="#000000",width=3)
#         self.canvas.create_line(5,548,550,548,fill="#000000",width=3)
#         self.canvas.create_line(187,5,187,548,fill="#000000",width=3)
#         self.canvas.create_line(366,5,366,548,fill="#000000",width=3)
#         self.canvas.create_line(5,186,548,186,fill="#000000",width=3)
#         self.canvas.create_line(5,366,548,366,fill="#000000",width=3)

#         self.delete_btn = Button(self.frame,
#             text="删除",
#             bg='white',
#             fg='black',
#             font=ft2,
#             command=self.delete_clicked)
#         self.delete_btn.place(x=720,y=58,width=150,height=58)

#         self.suggest_btn = Button(self.frame,
#             text="提示",
#             bg='white',
#             fg='black',
#             font=ft2,
#             command=self.hint_given)
#         self.suggest_btn.place(x=720,y=160,width=150,height=58)

#         self.finish_btn = Button(self.frame,
#             text="完成",
#             font=ft2,
#             bg='white',
#             fg='black',
#             command=self.win)
#         self.finish_btn.place(x=720,y=270,width=150,height=58)        

#         self.return_btn = Button(self.frame,
#             text="返回",
#             command=self.return_main,
#             bg='white',
#             fg='black',
#             font=ft2)
#         self.return_btn.place(x=720,y=520,width=150,height=58)        

#         self.continue_btn = Button(self.frame,
#             text="Continue",
#             font=ft2,
#             command=self.next_level)
        
#         self.counttime()

#         # self.next_btn.place(x=720,y=330,width=150,height=58)

#     # def counttime(self):
#     #     self._start = time.time()-self._elapsedtime
#     #     self._update()

#     # def _update(self):
#     #     """用逝去的时间更新标签"""
#     #     global msec
#     #     self._elapsedtime = time.time() - self._start
#     #     self._setTime(self._elapsedtime)
#     #     self._timer = self.frame.after(msec,self._update)

#     def counttime(self):
#         if self.rtime > 0:
#             self.rtime -= 1
#             self._setTime(self.rtime)
#             self.frame.after(1000,self.counttime) 
#         else:
#             self.ans_btn.place_forget()
#             self.continue_btn.place(x=720,y=380,width=150,height=58)

#     def _setTime(self,remaintime):
#         """将时间格式改为分:秒:百分秒"""
#         minutes = int(remaintime/60)
#         seconds = int(remaintime - minutes*60.0)
#         # hseconds = int((remaintime - minutes*60.0-seconds)*100)
#         # self.time.set('%02d:%02d' % (minutes,seconds))

#         if self.rtime <= 0:
#             self.time.set("Time Is Over")
#             for i in range(9):
#                 for j in range(9):
#                     map_btn[i][j].config(state="disabled")
#                     map_hide_btn[i][j] = 0
#         else:
#             self.time.set('%02d:%02d' % (minutes,seconds))

#     def win(self):
#         global map_btn
#         global map_normal

#         flag=[]

#         if self.rtime > 0:
#             for i in range(9):
#                 for j in range(9):
#                     if map_hide_btn[i][j] == 1:
#                         if map_btn[i][j]['text'] == map_normal[i][j]:
#                             flag.append(1)                        
#                         else:
#                             flag.append(0)

#             if flag.__contains__(0):
#                 self.time.set("Fall")
#             else:
#                 self.time.set("Win")
#                 self.rtime = -1                
#                 for i in range(9):
#                     for j in range(9):
#                         map_btn[i][j].config(state="disabled")

if __name__ == '__main__': 
    start = datetime.datetime.now()
    root = Tk()             #生成主窗口
    root.title("数独游戏")
    root.resizable(0,0)     #大小不可变

    normal_page(root)
    end = datetime.datetime.now()
    print(end-start)
    root.mainloop()