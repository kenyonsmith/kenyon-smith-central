#!/usr/bin/python

import datetime
import os
import sys
from operator import itemgetter
from six.moves import input

# codes for actions
TASK_NEW = 0
TASK_SWITCH = 1
TASK_COMPLETED = 2
TASK_WALK = 3
TASK_ADD_TASKS = 4
TASK_PAUSE = 5
TASK_LUNCH = 6
TASK_MEETING = 7
action_codes = ['NEW TASK', 'SWITCH TASK', 'COMPLETED TASK', 'WALK', 'ADD TASKS', 'PAUSE', 'LUNCH', 'IN MEETING']
timed_tasks = {TASK_NEW: False,
               TASK_SWITCH: True,
               TASK_COMPLETED: False,
               TASK_WALK: True,
               TASK_ADD_TASKS: True,
               TASK_PAUSE: True,
               TASK_LUNCH: True,
               TASK_MEETING: True}

# codes for task types
TASK_WORK_TYPE = 0
TASK_PERS_TYPE = 1
task_types = ['work', 'personal']

class Task:
    def __init__(self, name='no_name', time=0, task_type=TASK_WORK_TYPE, completed=False):
        self.name = name
        self.time = time
        self.task_type = task_type
        self.completed = completed

class Action:
    def __init__(self, action, task_id=-1, dt=None):
        self.action = action
        self.task_id = task_id
        if dt==None:
            self.dt = datetime.datetime.now()
        else:
            self.dt = dt

class Journal:
    def __init__(self):
        self.tasks = []
        self.cur_action = TASK_ADD_TASKS
        self.cur_action_key = -1
        self.actions = []

        self.read_from_file()
        self.add_action(TASK_ADD_TASKS)

    def write_to_file(self):
        with open("journal_tasks.txt",'w') as f:
            for task in self.tasks:
                f.write("{0},{1},{2},{3}\n".format(task.name, task.time, task.task_type, task.completed))
        with open("journal_actions.txt",'w') as f:
            for action in self.actions:
                f.write("{0},{1},{2}\n".format(action.action, action.task_id, action.dt))

    def read_from_file(self):
        if not os.path.exists('journal_tasks.txt'):
            with open("journal_tasks.txt", 'w') as f:
                pass
        if not os.path.exists('journal_actions.txt'):
            with open("journal_actions.txt", 'w') as f:
                pass
        with open("journal_tasks.txt",'r') as f:
            for task in f:
                data = task.strip().split(',')
                if len(data) == 4:
                    self.tasks.append(Task(data[0], int(data[1]), int(data[2]), data[3]=='True'))
        with open("journal_actions.txt",'r') as f:
            for action in f:
                data = action.strip().split(',')
                if len(data) == 3:
                    self.actions.append(Action(int(data[0]), int(data[1]), datetime.datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S.%f")))

    def add_task(self, name, num_minutes, task_type):
        self.tasks.append(Task(name=name, time=num_minutes, task_type=task_type))
        self.write_to_file()
        return len(self.tasks)-1

    def add_action(self, action, task_id=-1):
        self.actions.append(Action(action=action, task_id=task_id))
        self.write_to_file()
        return len(self.actions)-1

    def clear_data(self, ans):
        if 'y' not in ans:
            confirm = input("Really clear all data (y/n)? ".format())
        else:
            confirm = 'y'

        if confirm == 'y':
            os.remove('journal_tasks.txt')
            os.remove('journal_actions.txt')
            self.tasks = []
            self.actions = []
            self.cur_action = TASK_ADD_TASKS
            self.actions = []

            self.add_action(TASK_ADD_TASKS)

    def remove_last_action(self, ans):
        if len(self.actions)>0:
            # get last action
            action = self.actions[-1]
            if action.task_id != -1:
                action_name = '{0} {1} {2}, active for {3} minutes'.format(action.dt.strftime('%a %b %d %Y %X'), action_codes[action.action], self.task_str(action.task_id), int(self.count_time_in_action(TASK_SWITCH, action.task_id, None, None)/60))
            else:
                action_name = '{0} {1}'.format(action.dt.strftime('%a %b %d %Y %X'), action_codes[action.action])

            # ask for verifiction
            if 'y' not in ans:
                confirm = input("Really remove action {0} (y/n)? ".format(action_name))
            else:
                confirm = 'y'

            # remove it
            if confirm=="y":
                self.actions = self.actions[:-1]
                print("Action {0} removed.".format(action_name))

                # reset cur_action and cur_action_key
                if len(self.actions)>0:
                    next_action = self.actions[-1]
                    self.cur_action = next_action.action
                    self.cur_action_key = next_action.task_id
                else:
                    self.cur_action = TASK_ADD_TASKS
                    self.cur_action_key = -1
            else:
                print("Nothing was changed.")
        else:
            print("Error: No actions remaining.")

    def task_str(self, task_id):
        value = self.tasks[task_id]
        return '{0}{1}.{2} {3}'.format(task_types[value.task_type][0], task_id, value.time, value.name)

    def list_tasks(self, task_type=None):
        for key, value in enumerate(self.tasks):
            if task_type==None or value.task_type==task_type:
                if not value.completed:
                    print(self.task_str(key))

    def first_action(self, day_start=datetime.date.today(), num_days=1):
        """
        Consider a task only if it was after or on day_start, and within num_days
        Note that day_start and num_days may be None
        Default is to consider only today
        """
        min_day = datetime.datetime.now()
        for ix, action in enumerate(self.actions):
            if (day_start and (action.dt.date() < day_start)) or (num_days and (action.dt.date() >= (day_start+datetime.timedelta(days=num_days)))):
                continue
            if action.dt < min_day:
                min_day = action.dt
        return min_day.time()

    def count_time_in_action(self, action_type, action_key=-1, day_start=datetime.date.today(), num_days=1):
        """
        Consider a task only if it was after or on day_start, and within num_days
        Note that day_start and num_days may be None
        Default is to consider only today
        """
        total_time = 0
        for ix, action in enumerate(self.actions):
            if (day_start and (action.dt.date() < day_start)) or (num_days and (action.dt.date() >= (day_start+datetime.timedelta(days=num_days)))):
                continue
            if action.action==action_type and (action_key==-1 or action.task_id==action_key):
                # find the next action that is not a TASK_NEW or TASK_COMPLETED (timed_tasks=True)
                still_count = True
                incr = 1
                while still_count:
                    if (ix+incr)<len(self.actions):
                        a = self.actions[ix+incr].action
                        if timed_tasks[a]:
                            this_time = self.actions[ix+incr].dt - action.dt
                            still_count = False
                        else:
                            incr = incr+1
                    else:
                        # we are still doing this action
                        this_time = datetime.datetime.now() - action.dt
                        still_count = False
                total_time = total_time+this_time.seconds
        return total_time

    def count_overtime(self, day_start=datetime.date.today(), num_days=1):
        """
        Counts time spent over the allocated time given for a task, over the period given
        Returns a tuple (number of tasks that went overtime, total time overspent)
        """
        total_overtime = 0
        num_overtime = 0
        for ix, task in enumerate(self.tasks):
            expected_sec = 60*self.tasks[ix].time

            # Find out how much time has been spent on this action in all
            total_sec = self.count_time_in_action(TASK_SWITCH, ix, None, None)

            # Find out how much of that time was spent today
            today_sec = self.count_time_in_action(TASK_SWITCH, ix, day_start, num_days)

            # Find out how much is expected after work that wasn't done today
            adjusted_expected_sec = max(expected_sec - (total_sec - today_sec), 0)

            # Penalize only based on how much of that task was done today, only if it went over
            if total_sec > expected_sec and today_sec > adjusted_expected_sec:
                num_overtime = num_overtime + 1
                total_overtime = total_overtime + today_sec - adjusted_expected_sec
        return (num_overtime, total_overtime)

    def list_actions(self):
        ans = input("How many actions would you like to see? (1-{0}) ".format(len(self.actions)))
        if ans=='':
            ans='10'
        try:
            num_actions = int(ans)
        except ValueError:
            print("Was unable to convert {0} to an integer".format(ans))
            return

        if num_actions > len(self.actions):
            num_actions = len(self.actions)
        if num_actions < 1:
            num_actions = 1

        max_digits = len(str(len(self.actions)))
        print('{0}  DOW MON DY YEAR TIME     ACTION         TSK ESTIMTM ACTULTM'.format('#'*max_digits))
        for ix, action in enumerate(reversed(self.actions[(len(self.actions)-num_actions):])):
            realix = len(self.actions)-1-ix
            if action.task_id != -1:
                print('{0}{1}: {2} {3:<15}{4:>3} {5:>7} {6:>7}'.format(
                    ' '*(max_digits-len(str(realix))),
                    realix, action.dt.strftime('%a %b %d %Y %X'),
                    action_codes[action.action],
                    action.task_id,
                    self.tasks[action.task_id].time,
                    int(self.count_time_in_action(TASK_SWITCH, action.task_id, None, None)/60)))
            else:
                print('{0}{1}: {2} {3:<15}'.format(' '*(max_digits-len(str(realix))),
                    realix,
                    action.dt.strftime('%a %b %d %Y %X'),
                    action_codes[action.action]))

    def make_custom_report(self, day_start, num_days):
        report=[]
        longest_task_name = len("Adding new tasks")

        total_time = 0
        for ix, task in enumerate(self.tasks):
            act_time = self.count_time_in_action(TASK_SWITCH, ix, day_start, num_days)
            if act_time>0:
                task_name = self.task_str(ix)
                report.append((task_name,act_time))
                total_time = total_time + act_time
                if len(task_name)>longest_task_name:
                    longest_task_name=len(task_name)

        if longest_task_name > 100:
            longest_task_name = 100

        this_str = 'First action'
        time = self.first_action(day_start, num_days).replace(microsecond=0)
        print("{0}{1}{2}".format(this_str,
            ' '*(longest_task_name-len(this_str)+2),
            time.isoformat()))

        for this_str, act_time in report:
            print("{0}{1}{2} hours, {3} minutes, {4} seconds".format(this_str,
                ' '*(longest_task_name-len(this_str)+2), int(act_time / 3600), int(act_time / 60) % 60, act_time % 60))

        this_str = 'In meetings'
        act_time = self.count_time_in_action(TASK_MEETING, -1, day_start, num_days)
        if act_time>0:
            total_time = total_time + act_time
            print("{0}{1}{2} hours, {3} minutes, {4} seconds".format(this_str,
                ' '*(longest_task_name-len(this_str)+2), int(act_time / 3600), int(act_time / 60) % 60, act_time % 60))

        this_str = 'Adding new tasks'
        act_time = self.count_time_in_action(TASK_ADD_TASKS, -1, day_start, num_days)
        if act_time>0:
            total_time = total_time + act_time
            print("{0}{1}{2} hours, {3} minutes, {4} seconds".format(this_str,
                ' '*(longest_task_name-len(this_str)+2), int(act_time / 3600), int(act_time / 60) % 60, act_time % 60))

        this_str = 'Walking'
        act_time = self.count_time_in_action(TASK_WALK, -1, day_start, num_days)
        if act_time>0:
            total_time = total_time + act_time
            print("{0}{1}{2} hours, {3} minutes, {4} seconds".format(this_str,
                ' '*(longest_task_name-len(this_str)+2), int(act_time / 3600), int(act_time / 60) % 60, act_time % 60))

        this_str = 'Lunch'
        act_time = self.count_time_in_action(TASK_LUNCH, -1, day_start, num_days)
        if act_time>0:
            print("{0}{1}{2} hours, {3} minutes, {4} seconds".format(this_str,
                ' '*(longest_task_name-len(this_str)+2), int(act_time / 3600),int(act_time / 60) % 60, act_time % 60))

        num_overtime, act_time = self.count_overtime(day_start, num_days)
        if act_time > 0 and num_overtime > 0:
            this_str = 'Overtime: ({0}) tasks'.format(num_overtime)
            print("{0}{1}{2} hours, {3} minutes, {4} seconds".format(this_str,
                ' '*(longest_task_name-len(this_str)+2), int(act_time / 3600),int(act_time / 60) % 60, act_time % 60))

        print("Total working time: {0} hours, {1} minutes, {2} seconds".format(int(total_time / 3600),
            int(total_time / 60) % 60, total_time % 60))

    def today_report(self):
        self.make_custom_report(datetime.date.today(), 1)

    def calendar_report(self, num_days):
        data=[]
        days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']

        def print_str_13_chars(string, time):
            time /= 60
            if time > 60:
                string += '{0}hr '.format(int(time/60))
            string += '{0}min'.format(time%60)
            sys.stdout.write(string)
            sys.stdout.write(' '*(14-len(string)))

        td = datetime.date.today()
        num_days = ((((num_days+6)-1-(td.isoweekday() % 7))/7)*7)+1+(td.isoweekday() % 7)
        #num_days = 21 + (td.isoweekday() % 7) + 1
        for i in xrange(num_days):
            this_entry = {}
            day = datetime.date.today() - datetime.timedelta(days=num_days-i-1)
            this_entry['day'] = day
            this_entry['day_str'] = "{0} {1}".format(day.day, days[day.isoweekday() % 7])
            this_entry['time_meet'] = self.count_time_in_action(TASK_MEETING, -1, day, 1)
            this_entry['time_add'] = self.count_time_in_action(TASK_ADD_TASKS, -1, day, 1)
            this_entry['time_walk'] = self.count_time_in_action(TASK_WALK, -1, day, 1)
            this_entry['time_lunch'] = self.count_time_in_action(TASK_LUNCH, -1, day, 1)
            this_entry['time_switch'] = self.count_time_in_action(TASK_SWITCH, -1, day, 1)
            data.append(this_entry)

        print('|-------------------------------------------------------------------------------------------------|')

        it = 0
        while it <= len(data):
            # loop through each day and print day string
            for day in range(7):
                if (it+day)<len(data):
                    day_str = data[it+day]['day_str']
                    sys.stdout.write("| {0}{1}".format(day_str, (12-len(day_str))*' '))
            print('|')

            # loop through each day and print hours worked
            for day in range(7):
                if (it+day)<len(data):
                    print_str_13_chars("| + ", data[it+day]['time_switch'])
            print('|')

            # loop through each day and print hours worked
            for day in range(7):
                if (it+day)<len(data):
                    print_str_13_chars("| W ", data[it+day]['time_walk'])
            print('|')

            # loop through each day and print hours worked
            for day in range(7):
                if (it+day)<len(data):
                    print_str_13_chars("| A ", data[it+day]['time_add'])
            print('|')

            # loop through each day and print hours worked
            for day in range(7):
                if (it+day)<len(data):
                    print_str_13_chars("| L ", data[it+day]['time_lunch'])
            print('|')

            # loop through each day and print hours worked
            for day in range(7):
                if (it+day)<len(data):
                    print_str_13_chars("| M ", data[it+day]['time_meet'])
            print('|')

            # print separator
            sys.stdout.write('|_____________'*min(7, len(data)-it))
            print('|')

            # jump to next week
            it += 7

    def custom_report(self):
        ans = input("Go back how many days? ")
        try:
            num_days = int(ans)
        except ValueError:
            print("Was unable to convert {0} to an integer".format(ans))
            return

        ans = input("MENU: (t)asking total report, (c)alendar report: ")
        if ans=='t':
            self.make_custom_report(day_start=(datetime.date.today() - datetime.timedelta(days=num_days)), num_days=num_days)
        elif ans=='c':
            self.calendar_report(num_days)

    def adjust_timing(self):
        self.list_actions()
        which_ix = input("Which action would you like to adjust timing for? " )
        try:
            ix = int(which_ix)
        except ValueError:
            print("Was unable to convert {0} to an integer".format(which_ix))
            return

        if ix<0 or ix>=len(self.actions):
            print("Action #{0} is an invalid action".format(ix))
            return

        time = input("By how much time would you like to adjust this action? (+=forward, -=negative, format=[[HH:]MM:]SS: ")

        # backwards or forwards
        ix_change = 1
        if time[0]=='-':
            ix_change = -1
            time=time[1:]

        # parse the string
        num_colons = time.count(":")
        try:
            if num_colons==2:
                time = datetime.datetime.strptime(time, "%H:%M:%S").time()
                td = datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
            elif num_colons==1:
                time = datetime.datetime.strptime(time, "%M:%S").time()
                td = datetime.timedelta(minutes=time.minute, seconds=time.second)
            elif num_colons==0:
                td = datetime.timedelta(seconds=int(time))
        except ValueError:
            print("Was unable to convert {0} using the format [[HH:]MM:]SS.".format(time))
            return

        # get the new date time
        td = td * ix_change
        new_dt = self.actions[ix].dt + td

        # don't let anything be in the future
        if new_dt > datetime.datetime.now():
            print("You are trying to adjust timing into the future. Operation cancelled.")
            return

        # count the number of actions that will be displaced by this action
        still_counting = True
        displaced_counted = 0
        while still_counting:
            still_counting = False
            try_ix = ix + displaced_counted + ix_change
            if (try_ix < len(self.actions)) and (try_ix >= 0):
                if (((ix_change==1) and (self.actions[try_ix].dt < new_dt)) or ((ix_change==-1) and (self.actions[try_ix].dt > new_dt))):
                    displaced_counted = displaced_counted + 1
                    still_counting = True

        # confirm
        confirm = input("You will displace {0} actions if you continue. Continue? (y/n) ".format(displaced_counted))
        if confirm=='y':
            # update the given datetime
            self.actions[ix].dt = new_dt

            # sort remaining list by dt
            self.actions.sort(key=lambda x: x.dt)

            # reset cur_action and cur_action_key
            if len(self.actions)>0:
                next_action = self.actions[-1]
                self.cur_action = next_action.action
                self.cur_action_key = next_action.task_id
            else:
                self.cur_action = TASK_ADD_TASKS
                self.cur_action_key = -1
        else:
            print("Operation cancelled.")


def add_task(journal, ans_char):
    name = input("Give a name for the new task {0}: ".format(len(journal.tasks)))
    if len(name)>0:
        time = input("How many minutes do you estimate this task will take? ")
        task_type = TASK_WORK_TYPE if 'w' in ans_char else TASK_PERS_TYPE
        try:
            num_minutes = int(time)
            task_id = journal.add_task(name, num_minutes, task_type);
            journal.add_action(action=TASK_NEW, task_id=task_id)
            print("Added {3} task {0} ({1} mins): {2}".format(task_id, num_minutes, name, task_types[task_type]))
        except ValueError:
            print("Was unable to convert your input {0} to an integer. Nothing was changed.".format(time))
    else:
        print("No name was entered. Nothing was changed.")

def complete_query(journal, ans):
    if journal.cur_action == TASK_SWITCH:
        if 'y' in ans:
            done = 'y'
        elif 'n' in ans:
            done = 'n'
        else:
            done = input("Did you complete the task {0}? (y/n) ".format(journal.task_str(journal.cur_action_key)))
        if done.lower() == 'y':
            journal.tasks[journal.cur_action_key].completed = True
            journal.add_action(TASK_COMPLETED, journal.cur_action_key)
            print("Congratulations for completing task {0}!".format(journal.task_str(journal.cur_action_key)))
            difference = 60*journal.tasks[journal.cur_action_key].time - journal.count_time_in_action(TASK_SWITCH, journal.cur_action_key, None, None)
            if difference > 0:
                print("You beat your estimation by {0} minutes and {1} seconds!".format(int(difference/60), difference%60))
            else:
                print("You took {0} minutes and {1} seconds longer than estimated.".format(int((-difference)/60), (-difference)%60))
        elif done.lower() != 'n':
            print("Invalid character entered. Operation aborted.")
            return False
    return True

def switch_task(journal, ans):
    # if they were working on a task, ask if it is completed
    res = complete_query(journal, ans)
    if not res:
        return

    # look for w, p, k or a in the command
    if 'w' in ans:
        new_task = 'w'
    elif 'p' in ans:
        new_task = 'p'
    elif 'k' in ans:
        new_task = 'k'
    elif 'a' in ans:
        new_task = 'a'
    elif 'l' in ans:
        new_task = 'l'
    elif 'm' in ans:
        new_task = 'm'
    else:
        new_task = input("MENU: (w)ork task, (p)ers task, in (m)eeting, wal(k), (l)unch, (a)dd task mode: ")
    if new_task=='w' or new_task=='p':
        # try to get the index from the command
        try:
            task_id = int(''.join(x for x in ans if x in '1234567890'))
        except ValueError as e:
            journal.list_tasks(TASK_WORK_TYPE if new_task=='w' else TASK_PERS_TYPE)
            task_id = input("What task would you like to work on? ")

        # try to interpret what the user entered
        try:
            task_id = int(task_id)
        except ValueError as e:
            print("Was unable to convert your input {0} to an integer. Nothing was changed.".format(task_id))
            return

        # switch to the next task, if valid
        if task_id>=0 and task_id<len(journal.tasks):
            if journal.tasks[task_id].completed:
                un_complete_task = input("Task {0} has been marked as completed. Would you like to change its status to uncomplete? ".format(journal.task_str(task_id)))
                if un_complete_task.lower() != 'y':
                    print("Nothing was changed.")
                    return
                else:
                    journal.tasks[task_id].completed = False
            journal.add_action(TASK_SWITCH, task_id)
            journal.cur_action = TASK_SWITCH
            journal.cur_action_key = task_id
            print("Action set to {0}.".format(journal.task_str(task_id)))
        else:
            print("Task ID {0} was not recognized. Nothing was changed.".format(task_id))
    elif new_task=='m':
        journal.add_action(TASK_MEETING)
        journal.cur_action = TASK_MEETING
        journal.cur_action_key = -1
        print("Action set to IN MEETING")
    elif new_task=='a':
        journal.add_action(TASK_ADD_TASKS)
        journal.cur_action = TASK_ADD_TASKS
        journal.cur_action_key = -1
        print("Action set to ADD TASKS")
    elif new_task=='l':
        journal.add_action(TASK_LUNCH)
        journal.cur_action = TASK_LUNCH
        journal.cur_action_key = -1
        print("Action set to LUNCH. Buon appetito!")
    else:
        journal.add_action(TASK_WALK)
        journal.cur_action = TASK_WALK
        journal.cur_action_key = -1
        if new_task=='k':
            print("Action set to WALK.")
        else:
            print("The response {0} was unrecognized. Action was set to WALK.".format(new_task))

def switch_add_tasks(journal, ans):
    # if they were working on a task, ask if it is completed
    complete_query(journal, ans)

    journal.add_action(TASK_ADD_TASKS)
    journal.cur_action = TASK_ADD_TASKS
    journal.cur_action_key = -1
    print("Action set to ADD TASKS")

def switch_pause(journal, ans):
    # if they were working on a task, ask if it is completed
    complete_query(journal, ans)

    journal.add_action(TASK_PAUSE)
    journal.cur_action = TASK_PAUSE
    journal.cur_action_key = -1
    print("Action set to TASK_PAUSE")

def display_current_action(journal):
    total_time = 0
    if journal.cur_action == TASK_SWITCH:
        print("Working on {0} task {1}".format("work" if journal.tasks[journal.cur_action_key].task_type==TASK_WORK_TYPE else "personal", journal.task_str(journal.cur_action_key)))
        total_time = journal.count_time_in_action(journal.cur_action, journal.cur_action_key, None, None)
    elif journal.cur_action == TASK_WALK:
        print("Walking, get back to work soon!")
    elif journal.cur_action == TASK_ADD_TASKS:
        print("Adding tasks, dang there must be a lot of them!")
    elif journal.cur_action == TASK_LUNCH:
        print("Eating lunch. This pizza is sure delicious!")
    elif journal.cur_action == TASK_MEETING:
        print("In a meeting. That's what the 14th commandment is all about!")
    elif journal.cur_action == TASK_PAUSE:
        print("Paused.")
    act_time = journal.count_time_in_action(journal.cur_action, journal.cur_action_key)

    # only print total time if it's TASK SWITCH and it's different from today time
    if total_time==0 or act_time==total_time:
        print("Time spent working on current task: {0} hours, {1} minutes, {2} seconds".format(int(act_time/3600), int(act_time/60)%60, act_time%60))
    else:
        print("Time spent working on current task today: {0} hours, {1} minutes, {2} seconds".format(int(act_time/3600), int(act_time/60)%60, act_time%60))
        print("Time spent working on current task total: {0} hours, {1} minutes, {2} seconds".format(int(total_time/3600), int(total_time/60)%60, total_time%60))

def main():
    journal = Journal()

    running = True
    while running:
        ans = input(">>> ")
        if len(ans)>0:
            ans_char=ans[0]
        else:
            continue

        if ans_char=='l':
            journal.list_tasks()
        elif ans_char=='j':
            journal.list_actions()
        elif ans_char=='t':
            journal.today_report()
        elif ans_char=='r':
            journal.custom_report()
        elif ans_char=='w' or ans_char=='p':
            add_task(journal, ans_char)
            if 's' in ans:
                switch_task(journal, 's{0}{1}'.format(ans_char, len(journal.tasks)-1))
        elif ans_char=='s':
            switch_task(journal, ans)
        elif ans_char=='a':
            switch_add_tasks(journal, ans)
            if 'w' in ans or 'p' in ans:
                add_task(journal, ans)
                if 's' in ans:
                    ans = ans + str((len(journal.tasks)-1))
                    switch_task(journal, ans)
        elif ans_char=='c':
            display_current_action(journal)
        elif ans_char=='v':
            journal.remove_last_action(ans)
        elif ans_char=='d':
            journal.adjust_timing()
        elif ans_char=='z':
            switch_pause(journal, ans)
        elif ans_char=='x':
            journal.clear_data(ans)
        elif ans_char=='h':
            print("MENU: \ntask (l)ist\nadd (w)ork task\nadd (p)ersonal task\n(s)witch task\na(d)just timing\nremo(v)e last action\nprint (c)urrent action\nprint (t)oday's report\nprint (j)ournal\nprint custom (r)eport\npau(z)e\n(X) data\n(q)uit")
        elif ans_char=='q':
            switch_pause(journal, ans)
            running = False
        print('')

if __name__ == '__main__':
    main()
