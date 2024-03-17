from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import pickle
import random

#db connection imports
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('pg.env')

#athlete level model
level_fn = 'models/athlete_level.sav'
level = pickle.load(open(level_fn, 'rb'))

#distance factor model
dist_fn = 'models/dist_factor.sav'
dist_model = pickle.load(open(dist_fn, 'rb'))

#longest LR model
lr_fn = 'models/longest_lr.sav'
lr_model = pickle.load(open(lr_fn, 'rb'))

#load workouts
df_workouts = pd.read_csv('workouts/workouts.csv')

def mins_to_meters(m, s):
    base10_sec = round(s/60, 3)
    base10_min = m+base10_sec
    seconds = base10_min*60
    metersps = 1609.34/seconds
    return metersps

def minskm_to_meters(m, s):
    base10_sec = round(s/60, 3)
    base10_min = m+base10_sec
    seconds = base10_min*60
    metersps = 1000/seconds
    return metersps

def meters_to_mins(mps):
    sec_per_mile = round(1609.34/mps, 3)
    base10_min = sec_per_mile/60
    mins = int(base10_min)
    sec = round(base10_min%1, 3)*60
    return mins, sec

def meters_to_minskm(mps):
    sec_per_mile = round(1000/mps, 3)
    base10_min = sec_per_mile/60
    mins = int(base10_min)
    sec = round(base10_min%1, 3)*60
    return mins, sec

def pace_to_str(speed, unit):
    if unit=='mile':
        m, s = meters_to_mins(speed)
        mins = str(m)+':'
        secs = []
        if s < 10:
            secs.append('0' + str(int(round(s, 0))))
        else:
            secs.append(str(int(round(s, 0))))
        secs = secs[0] 
        pace_str = mins+secs+'/mile'
        return pace_str
    elif unit=='km':
        m, s = meters_to_minskm(speed)
        mins = str(m)+':'
        secs = []
        if s < 10:
            secs.append('0' + str(int(round(s, 0))))
        else:
            secs.append(str(int(round(s, 0))))
        secs = secs[0] 
        pace_str = mins+secs+'/km'  
        return pace_str

#function to date race date, number of weeks to train, and generate 
def get_calendar(date, weeks, speed, race_dist, units):
    
    #calcluate meters per second (speed) from goal pace
    speed=speed
    
    #handle weekday races (move mon-wed races to previous sun, move thurs-fri races to upcoming Sat)
    early={'mw':False, 'tf':False}
    #move mon-wed race back to previous sunday
    if date.weekday() <= 2:
        race_date = date - timedelta(days=(date.weekday()+1))
        early['mw']=True
    #move thur and fri races to upcoming sat
    elif date.weekday() in [3, 4]:
        race_date= date + timedelta(days=(5-date.weekday()))
        early['tf']=True
    else:
        race_date=date
        
    cal = weeks*7
    
    date_list = [(race_date + timedelta(days=1)) - timedelta(days=x) for x in range(1,(cal+1))]
    
    date_list.reverse()
    
    days = []

    for x in date_list:
        days.append(x.weekday())
        
    data = {'date': date_list, 'day_code': days}
    
    df_training_cal = pd.DataFrame(data)
    
    #create validation table for weekday codes/desc to join to training calendar
    weekdays = {'day_code': range(0,7), 'day_desc': ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']}
    df_weekdays = pd.DataFrame(weekdays)
    df_weekdays
    
    df_training_cal = pd.merge(df_training_cal, df_weekdays, how='left', on='day_code')
    
    #find first monday and crop calendar down to start on first monday
    first_mon = df_training_cal[df_training_cal.day_code == 0].index[0]
    df_training_cal = df_training_cal.iloc[first_mon:].reset_index(drop=True)
    
    #create column for week count
    week = []
    count = 0
    for index, row in df_training_cal.iterrows():
        if row.day_code == 0:
            count += 1
            week.append(count)
        else:
            week.append(count)
    df_training_cal['week']=week
    
    #create column for training phase
    #2 week taper for blocks under 14 weeks, 3 week taper for blocks >= 14 weeks
    block = 0
    if weeks < 14:
        block += (weeks - 2)
    if weeks >= 14:
        block += (weeks - 3)
    base = np.ceil(block*0.4)
    peak = np.floor(block*0.6)

    phase= []

    for index, row in df_training_cal.iterrows():
        if row.week <= base:
            phase.append('base')
        elif row.week-base <= peak:
            phase.append('peak')
        else:
            phase.append('taper')
    df_training_cal['phase']=phase
    df_training_cal.to_csv('weekday_race.csv', index=False)
    #calculate level and assign to level raw (used for pace calc)
    #if level raw is outside range(1,10), bound to nearest level and assign to dist_level (used for max distance calc)
    user_X = pd.DataFrame({'speed': [speed], 'distance': [race_dist]})
    level_raw = level.predict(user_X)[0]
    #dist_level = []
    
    if level_raw < 1:
        dist_level=1
    elif level_raw > 10:
        dist_level=10
    else:
        dist_level=level_raw
        
    #calculate paces (to be used for workouts)
    b1 = level.coef_[0]
    b2 = level.coef_[1]
    b0 = level.intercept_

    five_k = ((level_raw - b0) - (3.1*b2)) / b1
    ten_k = ((level_raw - b0) - (6.2*b2)) / b1
    hmp = ((level_raw - b0) - (13.1*b2)) / b1
    mp = ((level_raw - b0) - (26.2*b2)) / b1
    z2 = mp*0.825
    
    #weekly mileage peak
    mileage_max = 0
    if race_dist == 3.1:
        mileage_max += 45
    elif race_dist == 6.2:
        mileage_max += 50
    elif race_dist == 13.1:
        mileage_max += 60
    elif race_dist == 26.2:
        mileage_max += 75
        
    dist_factor = dist_model(dist_level) 

    user_max = mileage_max*dist_factor

    #user_max = mileage_max-(level_final[0]*3)
    
    #weekly mileage
    base = len(df_training_cal.loc[df_training_cal.phase=='base'].week.unique())
    peak = len(df_training_cal.loc[df_training_cal.phase=='peak'].week.unique())
    taper = len(df_training_cal.loc[df_training_cal.phase=='taper'].week.unique())
    
    week_1 = round(user_max/3, 1)
    build = user_max-week_1
    weekly_miles = []
    
    week_num = []
    
    for index, row in df_training_cal.iterrows():
        if row.week not in week_num:
            week_num.append(row.week)
            
    weekly_miles = [week_1]
    miles = 0
    
    for i in range(1,base):
        miles += build/(base-1)
        weekly_miles.append(round(week_1+miles, 1))
    
    for i in range(1, peak+1):
        weekly_miles.append(round(user_max, 1))
    
    if taper == 2:
        weekly_miles.append(user_max*0.7)
        weekly_miles.append(user_max*0.4)
        
    if taper == 3:
        weekly_miles.append(round(user_max*0.85, 1))
        weekly_miles.append(round(user_max*0.65, 1))
        weekly_miles.append(round(user_max*0.3, 1))
    
    data = {'week': week_num, 'mileage': weekly_miles}
    df_mileage = pd.DataFrame(data)
    
    #add weekly mileage into df_training_cal
    weekly_mileage = []
    for index, row in df_training_cal.iterrows():
        weekly_mileage.append(df_mileage.loc[df_mileage.week == row.week].mileage.values[0])
    
    df_training_cal["weekly_mileage"] = weekly_mileage
    
    #add down week for training blocks >= 14 weeks
    if weeks >= 14:
        down_phase = []
        down_mileage = []
        
        for index, row in df_training_cal.iterrows():
            if row.week == (base + (peak-2)):
                down_phase.append('down')
                down_mileage.append(round(user_max*0.5, 1))
            else:
                down_phase.append(row.phase)
                down_mileage.append(row.weekly_mileage)
                
        df_training_cal['phase']=down_phase
        df_training_cal['weekly_mileage']=down_mileage
        
    ###LONG RUNS###
    
    #establish max long run distance
    max_lr = 0
    if (race_dist == 3.1) and (user_max/3 <= 10):
        max_lr += round(user_max/3, 1)
    elif (race_dist == 3.1) and (user_max/3 > 10):
        max_lr += 10
    elif (race_dist == 6.2) and (user_max/3 <= 12):
        max_lr += round(user_max/3, 1)
    elif (race_dist == 6.2) and (user_max/3 > 12):
        max_lr += 12
    elif (race_dist == 13.1) and (user_max/3 <= 18):
        max_lr += round(user_max/3, 1)
    elif (race_dist == 13.1) and (user_max/3 > 18):
        max_lr += 18
    #for full-marathon, use linear model
    elif (race_dist == 26.2):
        max_lr += lr_model(dist_level)
    
    #max_lr = max_lr[0]
    lr_85pct = round(max_lr*0.85, 1)
    lr_90pct = round(max_lr*0.9, 1)
    lr_95pct = round(max_lr*0.95,1)
    base_lr = []
    lr1 = round(df_training_cal.loc[df_training_cal.week==1].weekly_mileage.unique()[0]/3, 1) #1/3 of first week total mileage,1)
    peak_lr = []
    down_lr = []
    postdown_lr = []
    taper_lr = []

    #base long runs
    base_step = (max_lr - lr1) / (base-1)
    base_lr_holder = lr1
    base_lr.append(lr1)

    for i in range(1,base):
        base_lr_holder+=base_step
        base_lr.append(round(base_lr_holder, 1))
    
    #if down week exists
    if weeks >= 14:
        #peak to down week long runs
        peak_lr.append(lr_85pct)
        down_week = df_training_cal.loc[df_training_cal.phase == 'down'].week.unique()[0]
        peak_weeks = len(df_training_cal.loc[(df_training_cal.phase == 'peak') & (df_training_cal.week < down_week)].week.unique())
        lr_diff = max_lr - lr_85pct
        step = lr_diff/(peak_weeks-1) 

        lr_holder = lr_85pct
        for i in range(1,peak_weeks):
            lr_holder+=step
            peak_lr.append(round(lr_holder, 1))
    
        #down week long run
        for index, row in df_training_cal.iterrows():
            if (row.day_code == 5) and (row.phase == 'down') and (row.weekly_mileage/3 < max_lr):
                down_lr.append(round(row.weekly_mileage/3, 1))

        #post down week peak long runs
        postdown_peak = len(df_training_cal.loc[(df_training_cal.phase == 'peak') & (df_training_cal.week > down_week)].week.unique())
        for i in range(1,postdown_peak+1):
            postdown_lr.append(lr_95pct)
    
    #if no down week
    else:
        peak_lr.append(lr_85pct)
        peak_weeks = len(df_training_cal.loc[(df_training_cal.day_code ==5) & (df_training_cal.phase == 'peak')])
        lr_diff = max_lr - lr_85pct
        step = lr_diff/(peak_weeks-1) 

        lr_holder = lr_85pct
        for i in range(1,peak_weeks):
            lr_holder+=step
            peak_lr.append(round(lr_holder, 1))
            
            
    #taper long runs
    for index, row in df_training_cal.iterrows():
        if (row.day_code == 5) and (row.phase == 'taper') and (row.weekly_mileage/3 < max_lr):
            taper_lr.append(round(row.weekly_mileage/3, 1))
        elif (row.day_code == 5) and (row.phase == 'taper') and (row.weekly_mileage/3 >= max_lr):
            taper_lr.append(lr_85pct)
            
    long_runs = base_lr + peak_lr + down_lr + postdown_lr + taper_lr
    
    #daily distance, run types, and run descriptions
    #runs per week
    runs_per_wk = []
    for index, row in df_training_cal.iterrows():    
        #if weekly mileage under 20, assign rest days to mon, fri, sun
        if (row.weekly_mileage < 21.99):
            runs_per_wk.append(4)
        #if weekly mileage btw 20 and 40, assign rest days to mon, fri
        elif (row.weekly_mileage >= 22) & (row.weekly_mileage < 39.99):
            runs_per_wk.append(5)
        #if weekly mileage btw 40 and 55, assign rest day to mon
        elif (row.weekly_mileage >= 40) & (row.weekly_mileage < 54.99):
            runs_per_wk.append(6)
        #plug in LR distance on saturdays
        else:
            runs_per_wk.append(7)
        
    df_training_cal['runs_per_week'] = runs_per_wk
    
    #dist, run type, run_desc
    distance = []
    run_type = []
    run_desc = []
    run_name = []

    for index, row in df_training_cal.iterrows():    
        #if 4 runs per week, assign rest days to mon, fri, sun
        if (row.runs_per_week == 4) & (row.day_code in [0, 4, 6]):
            distance.append(0)
            run_type.append('rest')
            run_desc.append('This is a rest day. Prioritize relaxation and recovery.')
            run_name.append('Rest Day')
    
        #if 5 runs per week, assign rest days to mon, fri
        elif (row.runs_per_week == 5) & (row.day_code in [0, 4]):
            distance.append(0)
            run_type.append('rest')
            run_desc.append('This is a rest day. Prioritize relaxation and recovery.')
            run_name.append('Rest Day')
        #if 6 runs per week, assign rest day to mon
        elif (row.runs_per_week == 6) & (row.day_code == 0):
            distance.append(0)
            run_type.append('rest')
            run_desc.append('This is a rest day. Prioritize relaxation and recovery.')
            run_name.append('Rest Day')
        
        #plug in LR distance on saturdays
        elif (row.day_code == 5) & (row.week != df_training_cal.week.max()) & (early['mw']==False):
            lr_index = row.week - 1
            distance.append(round(long_runs[lr_index], 1))
            run_type.append('long_run')
            run_desc.append('The goal of this run is to build endurance, not speed. Keep the effort easy and focus on completing the distance')
            run_name.append('Long Run')
        #fill the rest with easy days
        else:
            lr_index = row.week - 1
            filler_dist = (row.weekly_mileage - long_runs[lr_index])/(row.runs_per_week - 1)
            distance.append(round(filler_dist, 1))     
            run_type.append('easy')
            run_desc.append('This run should be easy enough that you could carry on a conversation throughout the run.')
            run_name.append('Easy Day')

        
    df_training_cal['distance'] = distance
    df_training_cal['run_type'] = run_type
    df_training_cal['run_desc'] = run_desc
    df_training_cal['run_name'] = run_name
    
    ##WORKOUT ASSIGNMENT##
    distance = df_training_cal.distance.tolist()
    run_type = df_training_cal.run_type.tolist()
    run_desc = df_training_cal.run_desc.tolist()
    run_name = df_training_cal.run_name.tolist()

    #if half-marathon or greater
    if race_dist >= 13.1:
        #filter workouts file to users distance
        df_user_wo=df_workouts.loc[df_workouts.race==race_dist]
        df_user_wo.to_csv('user_workouts.csv', index=False)
        
        easy = df_user_wo.loc[(df_user_wo.phase == 'base') & (dist_level >= df_user_wo.dist_level_min) & (dist_level <= df_user_wo.dist_level_max) & (df_user_wo.workout_type=='midweek')].index.tolist()
        hard = df_user_wo.loc[(df_user_wo.phase == 'speed') & (dist_level >= df_user_wo.dist_level_min) & (dist_level <= df_user_wo.dist_level_max) & (df_user_wo.workout_type=='midweek')].index.tolist()
        taper = df_user_wo.loc[(df_user_wo.phase == 'base') & (df_user_wo.dist_level_max<=5)].index.tolist()
    
        random.shuffle(easy)
        random.shuffle(hard)
        random.shuffle(taper)
    
        easy_seq = easy*4
        hard_seq = hard*4
        taper_seq = taper #only need one taper workout

        easy_counter=0
        hard_counter=0
        long_counter=0
    
        #if level >= 5: base phase has weekly w/o + easy LR
        #peak phase has weekly w/o and hard LR
        if level_raw >= 5:
            long = df_user_wo.loc[(df_user_wo.phase == 'speed') & (dist_level >= df_user_wo.dist_level_min) & (dist_level <= df_user_wo.dist_level_max) & (df_user_wo.workout_type=='long_run')].index.tolist()
            random.shuffle(long)
            long_seq = long*4
            for index, row in df_training_cal.iterrows():           
                if (row.phase in ['base', 'taper', 'down']) & (row.day_code == 2) & (row.week != df_training_cal.week.max()):
                    #update wednesday run_type, desc, and dist with easy_seq
                    distance[index]=df_user_wo.loc[easy_seq[easy_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[easy_seq[easy_counter]]['desc']
                    run_name[index]=df_user_wo.loc[easy_seq[easy_counter]]['name']
                    easy_counter+=1
                elif (row.phase == 'peak') & (row.day_code == 2):
                    #update wednesday run_type, desc, and dist with hard_seq
                    distance[index]=df_user_wo.loc[hard_seq[hard_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[hard_seq[hard_counter]]['desc']
                    run_name[index]=df_user_wo.loc[hard_seq[hard_counter]]['name']
                    hard_counter+=1
                #long run workouts from peak - 2 weeks out
                elif (row.phase in ['peak', 'taper']) & (row.day_code == 5) & (row.week <= df_training_cal.week.max()-2):
                    #update saturday run_type, desc, and dist with hard_seq
                    run_type[index]='long_workout'
                    run_desc[index]=df_user_wo.loc[long_seq[long_counter]]['desc']
                    run_name[index]=df_user_wo.loc[long_seq[long_counter]]['name']
                    long_counter+=1
                #deal with final week
                #add strides to easy days, make w/o lowest level, add race to race day
                elif row.week == df_training_cal.week.max():
                    if (row.run_type == 'easy') & (row.day_code != 2):
                        run_desc[index]='The majority of this run should be at your usual easy pace, but do 3-5 reps of 30-60 second efforts at your goal race pace in the final mile of the run.\
                        This will allow you to maintain your top-end fitness as you taper toward race day.'
                        run_name[index]='Easy + Strides'
                    elif row.day_code == 2:
                        distance[index]=df_user_wo.loc[taper_seq[0]]['distance']
                        run_type[index]='workout'
                        run_desc[index]=df_user_wo.loc[taper_seq[0]]['desc']
                        run_name[index]=df_user_wo.loc[taper_seq[0]]['name']
                #add race day to calendar
                if row.date == df_training_cal.date.max():
                    run_type[index]='race'
                    run_desc[index]='Race day has arrived! Be patient, stick to your plan, and trust in your training. Good luck!'
                    run_name[index]='Race Day'
                    distance[index]=race_dist
                else:
                    continue
                
        #if level < 5: base phase all easy
        #peak phase has weekly hard w/o and easy LRs
        #down and taper have easy w/o
        if level_raw < 5:
            for index, row in df_training_cal.iterrows():           
                if (row.phase == 'peak') & (row.day_code == 2):
                    #update wednesday run_type, desc, and dist with hard_seq
                    distance[index]=df_user_wo.loc[hard_seq[hard_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[hard_seq[hard_counter]]['desc']
                    run_name[index]=df_user_wo.loc[hard_seq[hard_counter]]['name']
                    hard_counter+=1
                elif (row.phase in ['taper', 'down']) & (row.day_code == 2) & (row.week != df_training_cal.week.max()):
                    #update wednesday run_type, desc, and dist with easy_seq
                    distance[index]=df_user_wo.loc[easy_seq[easy_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[easy_seq[easy_counter]]['desc']
                    run_name[index]=df_user_wo.loc[easy_seq[easy_counter]]['name']
                    easy_counter+=1
                #deal with final week
                #add strides to easy days, make w/o lowest level, add race to race day
                elif row.week == df_training_cal.week.max():
                    if (row.run_type == 'easy') & (row.day_code != 2):
                        run_desc[index]='The majority of this run should be at your usual easy pace, but do 3-5 reps of 30-60 second efforts at your goal race pace in the final mile of the run.\
                        This will allow you to maintain your top-end fitness as you taper toward race day.'
                        run_name[index]='Easy + Strides'
                    elif row.day_code == 2:
                        distance[index]=df_user_wo.loc[taper_seq[0]]['distance']
                        run_type[index]='workout'
                        run_desc[index]=df_user_wo.loc[taper_seq[0]]['desc']
                        run_name[index]=df_user_wo.loc[taper_seq[0]]['name']
                #add race day to calendar
                if row.date == df_training_cal.date.max():
                    run_type[index]='race'
                    run_desc[index]='Race day has arrived! Be patient, stick to your plan, and trust in your training. Good luck!'
                    run_name[index]='Race Day'
                    distance[index]=race_dist
                else:
                    continue
    
    #10k and under
    if race_dist <= 6.2:
        #filter workouts file to users distance
        df_user_wo=df_workouts.loc[df_workouts.race==race_dist]
        
        easy = df_user_wo.loc[(df_user_wo.phase == 'base') & (dist_level >= df_user_wo.dist_level_min) & (dist_level <= df_user_wo.dist_level_max)].index.tolist()
        hard = df_user_wo.loc[(df_user_wo.phase == 'speed') & (dist_level >= df_user_wo.dist_level_min) & (dist_level <= df_user_wo.dist_level_max)].index.tolist()
        taper = df_user_wo.loc[(df_user_wo.phase == 'base') & (df_user_wo.dist_level_max<=5)].index.tolist()
    
        random.shuffle(easy)
        random.shuffle(hard)
        random.shuffle(taper)
    
        easy_seq = easy*8
        hard_seq = hard*8
        taper_seq = taper #only need one taper workout

        easy_counter=0
        hard_counter=0
        long_counter=0
    
        #if level >= 5: base phase has weekly w/o + easy LR
        #peak phase has two weekly workouts and easy LR
        if level_raw >= 5:
            for index, row in df_training_cal.iterrows():           
                if (row.phase in ['base', 'down']) & (row.day_code == 2) & (row.week != df_training_cal.week.max()):
                    #update wednesday run_type, desc, and dist with easy_seq
                    distance[index]=df_user_wo.loc[easy_seq[easy_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[easy_seq[easy_counter]]['desc']
                    run_name[index]=df_user_wo.loc[easy_seq[easy_counter]]['name']
                    easy_counter+=1
                #peak phase = easy workout tues, hard workout thurs
                elif (row.phase == 'peak') & (row.day_code == 1):
                    #update wednesday run_type, desc, and dist with hard_seq
                    distance[index]=df_user_wo.loc[easy_seq[easy_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[easy_seq[easy_counter]]['desc']
                    run_name[index]=df_user_wo.loc[easy_seq[easy_counter]]['name']
                    easy_counter+=1
                elif (row.phase == 'peak') & (row.day_code == 3):
                    #update wednesday run_type, desc, and dist with hard_seq
                    distance[index]=df_user_wo.loc[hard_seq[hard_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[hard_seq[hard_counter]]['desc']
                    run_name[index]=df_user_wo.loc[hard_seq[hard_counter]]['name']
                    hard_counter+=1
                #taper phase - easy w/o tues thurs
                #peak phase = easy workout tues, hard workout thurs
                elif (row.phase == 'taper') & (row.day_code in [1, 3]) & (row.week != df_training_cal.week.max()):
                    #update wednesday run_type, desc, and dist with hard_seq
                    distance[index]=df_user_wo.loc[easy_seq[easy_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[easy_seq[easy_counter]]['desc']
                    run_name[index]=df_user_wo.loc[easy_seq[easy_counter]]['name']
                    easy_counter+=1
                #deal with final week
                #add strides to easy days, make w/o lowest level, add race to race day
                elif row.week == df_training_cal.week.max():
                    if (row.run_type == 'easy') & (row.day_code != 2):
                        run_desc[index]='The majority of this run should be at your usual easy pace, but do 3-5 reps of 30-60 second efforts at your goal race pace in the final mile of the run.\
                        This will allow you to maintain your top-end fitness as you taper toward race day.'
                        run_name[index]='Easy + Strides'
                    elif row.day_code == 2:
                        distance[index]=df_user_wo.loc[taper_seq[0]]['distance']
                        run_type[index]='workout'
                        run_desc[index]=df_user_wo.loc[taper_seq[0]]['desc']
                        run_name[index]=df_user_wo.loc[taper_seq[0]]['name']
                #add race day to calendar
                if row.date == df_training_cal.date.max():
                    run_type[index]='race'
                    run_desc[index]='Race day has arrived! Be patient, stick to your plan, and trust in your training. Good luck!'
                    run_name[index]='Race Day'
                    distance[index]=race_dist
                else:
                    continue
                
        #if level < 5: base phase all easy
        #peak phase has weekly hard w/o and easy LRs
        #down and taper have easy w/o
        if level_raw < 5:
            for index, row in df_training_cal.iterrows():           
                if (row.phase == 'peak') & (row.day_code == 2):
                    #update wednesday run_type, desc, and dist with hard_seq
                    distance[index]=df_user_wo.loc[hard_seq[hard_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[hard_seq[hard_counter]]['desc']
                    run_name[index]=df_user_wo.loc[hard_seq[hard_counter]]['name']
                    hard_counter+=1
                elif (row.phase in ['taper', 'down']) & (row.day_code == 2) & (row.week != df_training_cal.week.max()):
                    #update wednesday run_type, desc, and dist with easy_seq
                    distance[index]=df_user_wo.loc[easy_seq[easy_counter]]['distance']
                    run_type[index]='workout'
                    run_desc[index]=df_user_wo.loc[easy_seq[easy_counter]]['desc']
                    run_name[index]=df_user_wo.loc[easy_seq[easy_counter]]['name']
                    easy_counter+=1
                #deal with final week
                #add strides to easy days, make w/o lowest level, add race to race day
                elif row.week == df_training_cal.week.max():
                    if (row.run_type == 'easy') & (row.day_code != 2):
                        run_desc[index]='The majority of this run should be at your usual easy pace, but do 3-5 reps of 30-60 second efforts at your goal race pace in the final mile of the run.\
                        This will allow you to maintain your top-end fitness as you taper toward race day.'
                        run_name[index]='Easy + Strides'
                    elif row.day_code == 2:
                        distance[index]=df_user_wo.loc[taper_seq[0]]['distance']
                        run_type[index]='workout'
                        run_desc[index]=df_user_wo.loc[taper_seq[0]]['desc']
                        run_name[index]=df_user_wo.loc[taper_seq[0]]['name']
                #add race day to calendar
                if row.date == df_training_cal.date.max():
                    run_type[index]='race'
                    run_desc[index]='Race day has arrived! Be patient, stick to your plan, and trust in your training. Good luck!'
                    run_name[index]='Race Day'
                    distance[index]=race_dist
                else:
                    continue
            
    #update training cal with new run types, desc, and names
    df_training_cal['run_type'] = run_type
    df_training_cal['run_desc'] = run_desc
    df_training_cal['run_name'] = run_name
    df_training_cal['distance'] = distance
        
    #re-calc filler dist
    df1 = df_training_cal.loc[df_training_cal.run_type != 'easy'].groupby(['week']).agg({'weekly_mileage': 'first', 'distance':'sum'}).reset_index()
    df2 = df_training_cal.loc[df_training_cal.run_type == 'easy'].groupby(['week'])['week'].count().reset_index(name='easy_days')
    df1 = pd.merge(df1, df2, on='week', how='left')
    df1['easy_mileage']=(df1.weekly_mileage - df1.distance)/df1.easy_days
    #df1.to_csv('df_filler.csv', index=False)
    for index, row in df_training_cal.iterrows():
        if (row.run_type == 'easy') & (row.week != df_training_cal.week.max()):
            distance[index]=round(df1.loc[df1.week==row.week]['easy_mileage'].values[0], 1)    
        else:
            continue
                
    df_training_cal['distance'] = distance
    
    ##PACE ASSIGNMENT##
    #paces as strings
    z2_str=pace_to_str(z2, unit=units)
    mp_str=pace_to_str(mp, unit=units)
    hmp_str=pace_to_str(hmp, unit=units)
    tenk_str=pace_to_str(ten_k, unit=units)
    fivek_str=pace_to_str(five_k, unit=units)
        
    pace = []
    for index, row in df_training_cal.iterrows():
        #all easy runs and long runs at z2 pace
        if row.run_type in ['easy', 'long_run']:
            pace.append(z2_str)
        #workouts in base phase all at MP
        elif (row.phase=='base') & (row.run_type=='workout'):
            #if half-marathon or longer, base workouts at mp
            if race_dist >=13.1:
                pace.append(mp_str)
            #under half-marathon, base workouts at 10k pace
            else:
                pace.append(tenk_str)
        #workouts in speed, down, and taper phase at 10k-hmp
        elif (row.phase in ['peak', 'down', 'taper']) & (row.run_type=='workout'):
            if race_dist >=13.1:
                pace.append(tenk_str + ' - ' + hmp_str)
            else:
                pace.append(fivek_str + ' - ' + tenk_str)
        #lr workouts always at goal race pace. only apply to half and full
        elif row.run_type in ['long_workout', 'race']:
            pace.append(pace_to_str(speed, unit=units))
        else:
            #pace='-' for rest days
            pace.append('-')
                 
    df_training_cal['pace'] = pace
    
    #create km column for distance
    dist_km=[]
    for index, row in df_training_cal.iterrows():
        dist_km.append(round(row.distance*1.60934, 2))
    df_training_cal['dist_km']=dist_km
    
    #deal with weekday races
    if early['mw']==True:
        diff=date.weekday()+1
        date_list = [(date + timedelta(days=1)) - timedelta(days=x) for x in range(1,(diff+1))]
        date_list.reverse()
        race_data=df_training_cal.iloc[df_training_cal.index.stop-1]
        #exchange race day data for a repeat of the prior days run
        df_training_cal.at[df_training_cal.index.stop-1, 'distance'] = df_training_cal.iloc[df_training_cal.index.stop-2].distance
        df_training_cal.at[df_training_cal.index.stop-1, 'run_type'] = df_training_cal.iloc[df_training_cal.index.stop-2].run_type
        df_training_cal.at[df_training_cal.index.stop-1, 'run_desc'] = df_training_cal.iloc[df_training_cal.index.stop-2].run_desc
        df_training_cal.at[df_training_cal.index.stop-1, 'run_name'] = df_training_cal.iloc[df_training_cal.index.stop-2].run_name
        df_training_cal.at[df_training_cal.index.stop-1, 'pace'] = df_training_cal.iloc[df_training_cal.index.stop-2].pace
        df_training_cal.at[df_training_cal.index.stop-1, 'dist_km'] = df_training_cal.iloc[df_training_cal.index.stop-2].dist_km
        
        df_new={}
        for c in df_training_cal.columns:
            df_new[c]=[]
        for d in date_list:
            if d != date_list[-1]:
                df_new['date'].append(d)
                df_new['day_code'].append(d.weekday())
                df_new['day_desc'].append(df_weekdays.loc[df_weekdays.day_code==df_new['day_code'][-1]].day_desc.values[0])
                df_new['week'].append(df_training_cal.week.max()+1)
                df_new['phase'].append('taper')
                df_new['weekly_mileage'].append(0)
                df_new['runs_per_week'].append(0)
                df_new['distance'].append(df_training_cal.iloc[df_training_cal.index.stop-2].distance)
                df_new['run_type'].append(df_training_cal.iloc[df_training_cal.index.stop-2].run_type)
                df_new['run_desc'].append(df_training_cal.iloc[df_training_cal.index.stop-2].run_desc)
                df_new['run_name'].append(df_training_cal.iloc[df_training_cal.index.stop-2].run_name)
                df_new['pace'].append(df_training_cal.iloc[df_training_cal.index.stop-2].pace)
                df_new['dist_km'].append(df_training_cal.iloc[df_training_cal.index.stop-2].dist_km)
            else:
                df_new['date'].append(d)
                df_new['day_code'].append(d.weekday())
                df_new['day_desc'].append(df_weekdays.loc[df_weekdays.day_code==df_new['day_code'][-1]].day_desc.values[0])
                df_new['week'].append(df_training_cal.week.max()+1)
                df_new['phase'].append('taper')
                df_new['weekly_mileage'].append(0)
                df_new['runs_per_week'].append(0)
                df_new['distance'].append(race_data.distance)
                df_new['run_type'].append(race_data.run_type)
                df_new['run_desc'].append(race_data.run_desc)
                df_new['run_name'].append(race_data.run_name)
                df_new['pace'].append(race_data.pace)
                df_new['dist_km'].append(race_data.dist_km)
                
        df_new=pd.DataFrame(df_new)
        df_training_cal = pd.concat([df_training_cal, df_new])
        
    elif early['tf']==True:
        #get race day data
        race_data=df_training_cal.iloc[df_training_cal.index.stop-1]
        #get race date and crop df down to appropriate day
        i_race=df_training_cal.loc[df_training_cal.date==date].index.values[0]
        df_training_cal=df_training_cal.loc[:i_race]
        #exchange last day data for race day data
        df_training_cal.at[df_training_cal.index.stop-1, 'distance'] = race_data.distance
        df_training_cal.at[df_training_cal.index.stop-1, 'run_type'] = race_data.run_type
        df_training_cal.at[df_training_cal.index.stop-1, 'run_desc'] = race_data.run_desc
        df_training_cal.at[df_training_cal.index.stop-1, 'run_name'] = race_data.run_name
        df_training_cal.at[df_training_cal.index.stop-1, 'pace'] = race_data.pace
        df_training_cal.at[df_training_cal.index.stop-1, 'dist_km'] = race_data.dist_km
        #exchange workout wednesday for an easy day (based on tuesday of race week)
        i_easy = df_training_cal.loc[df_training_cal.day_code==1].index.max()
        easy=df_training_cal.loc[i_easy]
        i_wo=df_training_cal.loc[df_training_cal.day_code==2].index.max()
        
        df_training_cal.at[i_wo, 'distance'] = easy.distance
        df_training_cal.at[i_wo, 'run_type'] = easy.run_type
        df_training_cal.at[i_wo, 'run_desc'] = easy.run_desc
        df_training_cal.at[i_wo, 'run_name'] = easy.run_name
        df_training_cal.at[i_wo, 'pace'] = easy.pace
        df_training_cal.at[i_wo, 'dist_km'] = easy.dist_km
        
    return df_training_cal, level_raw, dist_level, user_max, df_mileage, \
            speed, five_k, ten_k, hmp, mp, z2, long_runs, max_lr, peak_lr, lr_85pct, race_dist


def check_user(username):
    conn = psycopg2.connect(host=os.getenv('ENDPOINT'), 
                            port=os.getenv('PORT'), 
                            database=os.getenv('DBNAME'), 
                            user=os.getenv('USER'), 
                            password=os.getenv('PWD'))
    cur = conn.cursor()
    cur.execute("SELECT * \
                FROM USERS \
                    WHERE EMAIL = \'" + username + "'")
    query_results = cur.fetchall()
    if len(query_results)==1:
        return True
    else:
        return False


def get_user(username): 
    conn = psycopg2.connect(host=os.getenv('ENDPOINT'), 
                            port=os.getenv('PORT'), 
                            database=os.getenv('DBNAME'), 
                            user=os.getenv('USER'), 
                            password=os.getenv('PWD'))
    cur = conn.cursor()
    cur.execute("SELECT * \
                FROM USERS \
                    WHERE EMAIL = \'" + username + "'")
    query_results = cur.fetchall()
    col_nms=[x.name for x in cur.description]
    df=pd.DataFrame(query_results)
    df.columns=col_nms
    return df

def new_user(first, last, email, hashed_pwd):
    conn = psycopg2.connect(host=os.getenv('ENDPOINT'), 
                            port=os.getenv('PORT'), 
                            database=os.getenv('DBNAME'), 
                            user=os.getenv('USER'), 
                            password=os.getenv('PWD'))
    cur = conn.cursor()
    cur.execute("INSERT INTO USERS (USER_ID, FIRST_NAME, LAST_NAME, EMAIL, PWD, TERMS, CREATED) \
                VALUES (DEFAULT, " +"'"+  first +"', '" + last +"', '"+ email +"', '"+ hashed_password +"', true, NOW());")
    conn.commit()
    
    cur.close()
    conn.close()

def createList(r1, r2):
    return [item for item in range(r1, r2+1)]

def createSec(r1, r2):
    temp = [item for item in range(r1, r2+1)]
    result = []
    for n in temp:
        if n < 10:
            result.append('0'+str(n))
        else:
            result.append(str(n))
    return result