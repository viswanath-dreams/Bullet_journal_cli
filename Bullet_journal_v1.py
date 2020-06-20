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

    def new_task(self,name):
        index=len(self.master_list)
        new_task=task(name)
        self.master_list.update({str(index+1):new_task.construct()})
        with open('app.json','w') as f:
            json.dump(self.master_list,f) 


    def migrate_task(self,task_number,migrate_days):
        notebook.check_task(self,task_number)
        curr_date=self.master_list[str(task_number-1)]['due_date']
        new_date=datetime.strptime(curr_date,'%Y-%m-%d').date()+timedelta(days=migrate_days)
        self.master_list[str(task_number-1)]["due_date"]=str(new_date)
        notebook.build(self)
    
    def delete_task(self,task_number):
        notebook.check_task(self,task_number)
        self.delete_list.update({str(len(self.delete_list)+1):self.master_list[str(task_number)]})
        with open('deleted_tasks.json','w') as f:
            json.dump(self.master_list[str(task_number)],f)
        del self.master_list[str(task_number)]
        notebook.build(self)

    def edit_tag(self,task_number,new_tag):
        notebook.check_task(self,task_number)
        self.master_list[str(task_number-1)]["tag"]=new_tag
        notebook.build(self)

    def show_all(self):
        temp_table(self.master_list,"sl.no","name","creation_date","due_date","tag").show()

    def show_deleted(self):
        temp_table(self.delete_list,"sl.no","name","creation_date","due_date","tag").show()

    def show_today(self):
        today_list={}
        for key,value in self.master_list.items():
            if datetime.strptime(value["due_date"],'%Y-%m-%d').date() == date.today():
                today_list.update({value["name"]:value["tag"]})
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
        with open('deleted_tasks.json','w') as f1:
            json.dump(self.delete_list,f1) 

commands={  
        "n":"Create new task",
        "d":"delete task. delete_task(sl.no)",
        "m":"move/migrate to different date. migrate_task(task number, no. of days to move)",
        "e":"edit default tag. edit_tag(sl number, tag)",
        "s_today":"show todays tasks",
        "s_all":"show all tasks",
        "s_del":"show deleted tasks only",
        "help":"invoke command list",
        "ctrl+c":"exit the program"
    }

def switch(case,notebook):
    if case == 'n':
        name=input("Please enter task name")
        notebook.new_task(str(name))
    elif case == 'd':
        number=input("Please enter sl no of task to be deleted")
        notebook.delete_task(int(number))
    elif case == 'm':
        number=input("Please enter sl no of task to be migrated")
        days_move=input("Please enter the no. of days to be added to task")
        notebook.migrate_task(int(number),int(days_move))
    elif case == 'e':
        number=input("Please enter sl no of task to be tagged")
        tag=input("Please enter the new tag")
        notebook.edit_tag(int(number),str(tag))
    elif case == 's_today':
        notebook.show_today()
    elif case == 's_all':
        notebook.show_all()
    elif case =='s_del':
        notebook.show_deleted()
    else:
        raise Exception("Invalid Command - Please check command list")

def help():
    help_table=temp_table(commands,"Command","Description")
    help_table.show()

def mainloop():
    my_notebook=notebook()
    try:
        while True:
            option=input("What would you like to do?")
            if option == "help":
                help()
            else:
                data=switch(str(option),my_notebook)
                
    except KeyboardInterrupt:
        print("\n******************* ",end="")
        print("exiting program *******************\n")

if __name__ == "__main__":
    print("**********Bullet Journal Alpha Verison -- viswanath**********")
    print("**************************************************************")
    help()
    mainloop()


    