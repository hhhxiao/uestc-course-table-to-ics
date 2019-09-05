# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import pytz
import re
from datetime import datetime, tzinfo,timedelta
from ics import Calendar,Event

#3 test passed
def get_table_info():
    soup = BeautifulSoup(open('courseTable.html'),'lxml')
    tables =  soup.find_all('table')
    table = None
    for item in tables:
        if 'id' in item.attrs:
            if item['id'] == 'manualArrangeCourseTable':
                table = item
                break

    course = [["" for i in range(7)] for i in range(12)]
    trs =  table('tbody')[0].find_all('tr')
    for i in range(12):#每一个tr是一节课
        tds = trs[i].find_all('td')#每一个星期是一个td,tds的长度是８,跳过长度不是８的
        if len(tds) == 8:
            for j in range(7):
                if 'rowspan' in tds[j+1].attrs:
                    num = tds[j+1]['rowspan']
                    course[i][j] = tds[j+1].get_text()+' '+num
    return course

#
# bug１：部分课程名字解析错误
def parse_item(item:str,i,j):
    ss = item.split(' ')
    teacher_name = ss[0]
    course_num = int(ss[2])
    pattern = re.compile(r'[(](.*?)[)]', re.S)
    strs = re.findall(pattern,ss[1])
    when_and_where = strs[1].split(',')
    where = when_and_where[1]
    when = when_and_where[0].split('-')
    begin_week = int(when[0])
    end_week = int(when[1])
    course_name_len = len(ss[1]) - len(strs[0]) - len(strs[1])-4
    course_name = ss[1][0:course_name_len]
    print('str',item,'course_name',course_name)
    #print('ss[1s]',ss[1],'name',course_name)
    return {
            'name':course_name,
            'teacher':teacher_name,
            'location':where,
            "begin_time":i+1,
            'week':j+1,
            "num":course_num,
            'begin_week':begin_week,
            'end_week':end_week
            }

def get_events(item):
    time_table = [
         [8,30], #1
         [10,20], #3
         [14,30], #5
         [16,20], #7
         [19,30] #9
         ]
    course_long = [0,0,95,145,205]
    begin_time = time_table[item['begin_time']//2]

    event_list = [] 
    for i in range(item['begin_week'],item['end_week']+1):
        b_time = datetime(2019,9,2,begin_time[0],begin_time[1],0)+timedelta(hours=-8,days=item['week']-1,weeks=i-1)
        e_time = b_time+timedelta(minutes = course_long[item['num']])
        ##print(b_time,'-------',e_time)
        e = Event()
        e.name = item['name']
        e.location = item['location']
        e.begin = str(b_time)
        e.end = str(e_time)
        event_list.append(e)
    return event_list

#test  passed
def parse_course(c):
    #item_table = [[[] for i in range(7)] for i in range(12)]
    event_list = []
    # str的条目格式
    # '罗建超 软件工程(R0823930.04)(1-13,品学楼A411) 3
    for i in range(12): #i是第i+1节课
        for j in range(7):#j是第星期　j+1
            if( c[i][j] != ""):
                #2014-01-01 00:00:00
                #2019-10-01 09:20:00
                event_list.append(parse_item(c[i][j],i,j))
    return event_list


def get_ics_file():
    c =Calendar()
    event_list =  parse_course(get_table_info())
    for item in event_list:
        print(item,'\n')
        for event in get_events(item):
            c.events.add(event)
    with open('course.ics', 'w') as my_file:
        my_file.writelines(c)


if __name__ == "__main__":
    get_ics_file()