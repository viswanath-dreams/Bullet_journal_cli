import json
from datetime import date
from datetime import timedelta
from datetime import datetime
import os
import time

class temp_table:

    def __init__(self,raw_table,*args):
        dump=[]
        ext_dict={}
        for item in raw_table:
            if type(raw_table[item]) is dict:
                for subitem in raw_table[item]:
                    dump.append(raw_table[item][subitem])
            else:
                dump.append(raw_table[item])
            ext_dict.update({item:dump})
            dump=[]

        self.table=ext_dict
        self.curr_name_len=0
        for names,values in self.table.items():
            self.index=[0]*len(values)

        self.head_lengths=[]
        self.head_names=[]
        for description in args:
            self.head_names.append(description)
            self.head_lengths.append(len(description))

    def heading(self):
        
        for i in range(0,len(self.head_lengths)):
            if i == 0:
                if self.head_lengths[i]>=self.curr_name_len:
                    self.curr_name_len=self.head_lengths[i]
                else:
                    pass
            else:
                if self.head_lengths[i]>=self.index[i-1]:
                    self.index[i-1]=self.head_lengths[i]


    def tab_build(self):
        for names,values in self.table.items():
            if len(names)>=self.curr_name_len:
                self.curr_name_len=len(names)
            for i in range(0,len(values)):
                if len(values[i])>=self.index[i]:
                    self.index[i]=len(values[i])
        #print(self.curr_name_len,self.index)

    def show(self):
        temp_table.tab_build(self)
        temp_table.heading(self)
        h_string="|"+self.head_names[0].ljust(self.curr_name_len)+"|"
        for i in range(1,len(self.head_names)):
            h_string=h_string+self.head_names[i].ljust(self.index[i-1])+"|"
        print(h_string)
        for names,values in self.table.items():
            p_string="|"+names.ljust(self.curr_name_len)+"|"
            for i in range(0,len(values)):
                p_string=p_string+values[i].ljust(self.index[i])+"|"
            print(p_string)

class task:
    def __init__(self,name):
        self.name=name
        self.creation_date=date.today()
        self.due_date=self.creation_date+timedelta(days=1)
        self.tag="none"

    def construct(self):
        self.thing={
                    "name":self.name,
                    "creation_date":str(self.creation_date),
                    "due_date":str(self.due_date),
                    "tag":self.tag
                    }
        return self.thing


class notebook():

    def __init__(self):
        if os.path.exists('app.json') is True:
            with open('app.json', 'r') as openfile:
                self.master_list=json.load(openfile)
        else:
            self.master_list={}
        if os.path.exists('deleted_tasks.json') is True:
            with open('deleted_tasks.json', 'r') as openfile_1:
                self.delete_list=json.load(openfile_1)
        else:
            self.delete_list={}

    def new_task(self,name,kwargs):
        index=len(self.master_list)
        new_task=task(name)
        self.master_list.update({str(index+1):new_task.construct()})
        if len(kwargs)>0:
            for key,value in kwargs.items():
                if key == "due_date":
                    self.master_list[str(index+1)]["due_date"]=datetime.strptime(str(value),'%y-%m-%d').strftime('%Y-%m-%d')
                if key == "tag":
                    self.master_list[str(index+1)]["tag"]=str(value)

        with open('app.json','w') as f:
            json.dump(self.master_list,f) 


    def migrate_task(self,task_number,migrate_days):
        try:
            notebook.check_task(self,task_number)
            curr_date=self.master_list[str(task_number)]['due_date']
            new_date=datetime.strptime(curr_date,'%Y-%m-%d').date()+timedelta(days=migrate_days)
            self.master_list[str(task_number)]["due_date"]=str(new_date)
            notebook.build(self)
        except:
            print("Please enter valid task number")

    def delete_task(self,task_number):
        try:
            notebook.check_task(self,task_number)
            self.delete_list.update({str(len(self.delete_list)+1):self.master_list[str(task_number)]})
            with open('deleted_tasks.json','w') as f:
                json.dump(self.master_list[str(task_number)],f)
            del self.master_list[str(task_number)]
            notebook.renumber(self)
            notebook.build(self)
        except:
            print("PLease enter valid task number")
        # try:
        #     notebook.check_task(self,task_number)
        #     self.delete_list.update({str(len(self.delete_list)+1):self.master_list[str(task_number)]})
        #     with open('deleted_tasks.json','w') as f:
        #         json.dump(self.master_list[str(task_number)],f)
        #     del self.master_list[str(task_number)]
        #     notebook.renumber(self)
        #     notebook.build(self)
        # except:
        #     print("Please enter valid task number")

    def edit_tag(self,task_number,new_tag):
        try:
            notebook.check_task(self,task_number)
            self.master_list[str(task_number)]["tag"]=new_tag
            notebook.build(self)
        except:
            print("Please enter valid task number")

    def show_all(self):
        clear_screen()
        temp_table(self.master_list,"sl.no","name","creation_date","due_date","tag").show()

    def show_deleted(self):
        if len(self.delete_list) <1:
            print("No items have been deleted")
        else:
            clear_screen()
            temp_table(self.delete_list,"sl.no","name","creation_date","due_date","tag").show()

    def show_today(self):
        today_list={}
        for key,value in self.master_list.items():
            if datetime.strptime(value["due_date"],'%Y-%m-%d').date() == date.today():
                today_list.update({value["name"]:value["tag"]})
        clear_screen()
        temp_table(today_list,"name","tag").show()

    def check_task(self,task_number):
        flag=0
        for key in self.master_list:
            if key == str(task_number):
                flag = 1
                break
        if flag == 1:
            pass
        else:
            raise Exception("Invalid task number")


    def build(self):
        with open('app.json','w') as f:
            json.dump(self.master_list,f) 
        # with open('deleted_tasks.json','w') as f1:
        #     json.dump(self.delete_list,f1) 
    
    def renumber(self):
        old_keys=[]
        for key in self.master_list:
            old_keys.append(int(key))
        new_keys=[]
        new_keys.append(old_keys[0])
        for i in range(1,len(old_keys)):
            if abs(old_keys[i]-new_keys[i-1])>1 or abs(old_keys[i]-new_keys[i-1])==0 :
                new_keys.append(new_keys[i-1]+1)
            else:
                new_keys.append(old_keys[i])
        str_keys=[]
        for i in range(0,len(new_keys)):
            str_keys.append(str(new_keys[i]))
        self.master_list=dict(zip(str_keys,list(self.master_list.values())))

commands={  
        "n":"Create new task",
        "d":"delete task. delete_task(sl.no)",
        "m":"move/migrate to different date. migrate_task(task number, no. of days to move)",
        "e":"edit default tag. edit_tag(sl number, tag)",
        "s_t":"show todays tasks",
        "s":"show all tasks",
        "s_del":"show deleted tasks only",
        "help":"invoke command list",
        "ctrl+c":"exit the program"
    }


def switch(case,notebook):
    if case == 'n':
        args={}
        in_cmd=input("Please enter task name(optional tag,due_date). Format <name>,<due_date=yy-mm-dd>,<tag=new_tag>: ").replace(" ","").split(',')
        if len(in_cmd)>1:
            for i in range(1,len(in_cmd)):
                key,val=in_cmd[i].split('=')
                args.update({key:val})
        notebook.new_task(in_cmd[0],args)   
    elif case == 'd':
        number=input("Please enter sl no of task to be deleted: ")
        notebook.delete_task(int(number))
    elif case == 'm':
        number,days_move=input("Please enter sl no of task, no. of days to be added to task. format: <sl.no>,<days_move>: ").split(',')
        notebook.migrate_task(int(number),int(days_move))
    elif case == 'e':
        number,tag=input("Please enter sl no of task, new tag. format: <sl.no>,<tag>: ").split(',')
        notebook.edit_tag(int(number),str(tag))
    elif case == 's_t':
        notebook.show_today()
    elif case == 's':
        notebook.show_all()
    elif case =='s_del':
        notebook.show_deleted()
    else:
        raise Exception("Invalid Command - Please check command list")
def help():
    help_table=temp_table(commands,"Command","Description")
    help_table.show()
    print("")

def clear_screen():
    os.system('cls')

def mainloop():
    my_notebook=notebook()
    try:
        while True:
            print()
            option=input("What would you like to do?")
            print("")
            if option == "help":
                help()
            else:
                try:
                    data=switch(str(option),my_notebook)
                except:
                    print("Invalid selection, Please re-enter command")
                    print("")
                    help()
                
    except KeyboardInterrupt:
        print("\n******************* ",end="")
        print("exiting program *******************\n")

if __name__ == "__main__":
    print("**********Bullet Journal Alpha Verison -- viswanath**********")
    print("**************************************************************")
    help()
    mainloop()