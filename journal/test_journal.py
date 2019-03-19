#!/usr/bin/python

import unittest
import os
import sys
try:
    from StringIO import StringIO
except ModuleNotFoundError:
    from io import StringIO

from contextlib import contextmanager

import journal
import datetime

# override print
class writer :
    def __init__(self, *writers) :
        self.__writers__ = writers

    def write(self, text):
        for w in self.__writers__ :
            w.write(text)

saved = sys.stdout
printed = StringIO()
sys.stdout = writer(sys.stdout, printed)

def mock_input(mock):
    if type(mock)==type(''):
        return mock
    elif type(mock)==type({}):
        def return_val(i):
            for k in mock.keys():
                if k in i:
                    return mock[k]
            return ''

        __builtins__.raw_input = return_val

# override raw_input

@contextmanager
def mockRawInput(mock):
    """ USAGE
    If you only need to call this once in your test,
    'mock' should be the expected answer from raw_input.
    If you need to call this multiple times, 'mock' should be a dictionary
    where keys are strings contained in each individual raw_input request,
    and values are the expected answer for that specific raw_input call.
    """

    # save original
    #original_raw_input = __builtins__.raw_input
    original_raw_input = __builtins__.raw_input

    # if single string
    if type(mock)==type(''):
        __builtins__.raw_input = lambda _: mock
    elif type(mock)==type({}):
        def return_val(i):
            for k in mock.keys():
                if k in i:
                    return mock[k]
            return ''

        __builtins__.raw_input = return_val
    else:
        assert False, "Unrecognized mock type: {0}".format(type(mock))

    yield
    __builtins__.raw_input = original_raw_input

class JournalController(unittest.TestCase):
    def setUp(self):
        # mock input
        self.input_values = []
        self.save_input = journal.input
        def mock_input(s):
            return self.input_values.pop(0)
        journal.input = mock_input

        # save files
        os.rename("journal_tasks.txt", "sjt.txt")
        os.rename("journal_actions.txt", "sja.txt")

        with open("journal_tasks.txt", 'w') as f:
            pass
        with open("journal_actions.txt", 'w') as f:
            pass

        self.journal = journal.Journal()

    def tearDown(self):
        journal.input = self.save_input
        os.remove("journal_tasks.txt")
        os.remove("journal_actions.txt")
        os.rename("sjt.txt", "journal_tasks.txt")
        os.rename("sja.txt", "journal_actions.txt")
        printed.truncate(0)

    def test_journal_add_task(self):
        self.journal.add_task("Hello!", 5, journal.TASK_PERS_TYPE)
        self.assertEqual(len(self.journal.tasks), 1)
        self.assertEqual(self.journal.tasks[0].name, "Hello!")
        self.assertEqual(self.journal.tasks[0].time, 5)
        self.assertEqual(self.journal.tasks[0].task_type, journal.TASK_PERS_TYPE)
        self.assertEqual(self.journal.tasks[0].completed, False)

    def test_journal_add_action(self):
        self.journal.add_action(journal.TASK_WORK_TYPE, 0)
        self.assertEqual(self.journal.actions[-1].action, journal.TASK_WORK_TYPE)
        self.assertEqual(self.journal.actions[-1].task_id, 0)
        self.assertTrue((datetime.datetime.now() - self.journal.actions[0].dt) < datetime.timedelta(hours=1))

    def test_journal_remove_last_action_no_actions(self):
        self.journal.actions = []
        self.journal.remove_last_action('')

        self.assertTrue("Error" in printed.getvalue())

    def test_journal_remove_last_action_confirm_yes(self):
        self.input_values.append('y')
        self.journal.remove_last_action('')

        self.assertEqual(0, len(self.journal.actions))

    def test_add_task(self):
        self.input_values.append('My Cool Task')
        self.input_values.append('14')
        journal.add_task(self.journal, "w")
        self.assertEqual(1, len(self.journal.tasks))
        self.assertEqual("My Cool Task", self.journal.tasks[0].name)
        self.assertEqual(14, self.journal.tasks[0].time)
        self.assertEqual(journal.TASK_WORK_TYPE, self.journal.tasks[0].task_type)
        self.assertEqual(False, self.journal.tasks[0].completed)

    def test_add_task_invalid_time(self):
        self.input_values.append('My Cool Task')
        self.input_values.append('')
        journal.add_task(self.journal, "w")
        self.assertEqual(0, len(self.journal.tasks))
        self.assertTrue("unable" in printed.getvalue())

    def test_list_tasks(self):
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.list_tasks()
        printed_lines = printed.getvalue().strip().split('\n')
        self.assertEqual(1, len(printed_lines))
        self.assertTrue("test_task" in printed_lines[0])

    def test_count_time_in_action_switch_noprevious_nocurrent_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=5)))
        self.journal.actions.append(journal.Action(action=journal.TASK_COMPLETED, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=4)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=3)))
        time = self.journal.count_time_in_action(journal.TASK_SWITCH, 0)
        self.assertEqual(2, time/60)

    def test_count_time_in_action_switch_noprevious_yescurrent_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=5)))
        time = self.journal.count_time_in_action(journal.TASK_SWITCH, 0)
        self.assertEqual(5, time/60)

    def test_count_time_in_action_walk_noprevious_yescurrent_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=5)))
        time = self.journal.count_time_in_action(journal.TASK_WALK, -1)
        self.assertEqual(5, time/60)

    def test_count_time_in_action_walk_noprevious_nocurrent_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=5)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=3)))
        time = self.journal.count_time_in_action(journal.TASK_WALK, -1)
        self.assertEqual(2, time/60)

    def test_count_time_in_action_switch_yesprevious_yescurrent_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=8)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=5)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=3)))
        time = self.journal.count_time_in_action(journal.TASK_SWITCH, -1)
        self.assertEqual(6, time/60)

    def test_count_time_in_action_switch_yesprevious_yescurrent_alltime(self):
        self.journal.actions[0].dt -= datetime.timedelta(days=1, minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=40, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(days=1, minutes=36)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(days=1)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=8)))
        time = self.journal.count_time_in_action(journal.TASK_SWITCH, 0, None, None)
        self.assertEqual(44, time/60)

    def test_count_time_in_action_switch_yesprevious_yescurrent_24hours(self):
        self.journal.actions[0].dt -= datetime.timedelta(days=2, minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=40, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(days=2, minutes=36)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(days=2, minutes=12)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(days=1, minutes=8)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(days=1)))
        time = self.journal.count_time_in_action(journal.TASK_SWITCH, 0, datetime.date.today()-datetime.timedelta(days=1), None)
        self.assertEqual(8, time/60)

    def test_overtime_no_overtime(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=5, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=4)))
        num_overtime, time_overtime = self.journal.count_overtime()
        self.assertEqual(num_overtime, 0)
        self.assertEqual(time_overtime, 0)

    def test_overtime_overtime_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=5, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=36)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=26)))
        num_overtime, time_overtime = self.journal.count_overtime()
        self.assertEqual(num_overtime, 1)
        self.assertEqual(time_overtime, 5*60)

    def test_overtime_overtime_yesterday(self):
        self.journal.actions[0].dt -= datetime.timedelta(days=1, minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=5, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(days = 1, minutes=36)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(days = 1, minutes=26)))
        num_overtime, time_overtime = self.journal.count_overtime(datetime.date.today(), 1)
        self.assertEqual(num_overtime, 0)
        self.assertEqual(time_overtime, 0)

    def test_overtime_overtime_yesterday_and_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(days=1, minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=5, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(days = 1, minutes=36)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(days = 1, minutes=26)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=26)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=16)))
        num_overtime, time_overtime = self.journal.count_overtime(datetime.date.today(), 1)
        self.assertEqual(num_overtime, 1)
        self.assertEqual(time_overtime, 10*60)

    def test_overtime_work_yesterday_overtime_today(self):
        self.journal.actions[0].dt -= datetime.timedelta(days=1, minutes=36)
        self.journal.tasks.append(journal.Task(name='test_task', time=15, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(days = 1, minutes=36)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(days = 1, minutes=26)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=26)))
        self.journal.actions.append(journal.Action(action=journal.TASK_PAUSE, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=16)))
        num_overtime, time_overtime = self.journal.count_overtime(datetime.date.today(), 1)
        self.assertEqual(num_overtime, 1)
        self.assertEqual(time_overtime, 5*60)

    def test_list_actions(self):
        self.input_values.append('1')
        self.journal.list_actions()
        printed_lines = printed.getvalue().strip().split('\n')
        self.assertEqual(2, len(printed_lines))

    def test_list_actions_no_input(self):
        self.input_values.append('')
        self.journal.list_actions()
        printed_lines = printed.getvalue().strip().split('\n')
        self.assertEqual(2, len(printed_lines))

    def test_list_actions_bad_input(self):
        self.input_values.append('Hello World!')
        self.journal.list_actions()
        printed_lines = printed.getvalue().strip().strip('\x00')
        self.assertEqual("Was unable to convert Hello World! to an integer", printed_lines)

    def test_list_actions_select_some(self):
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now()))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now()))
        self.input_values.append('2')
        self.journal.list_actions()
        printed_lines = printed.getvalue().strip().split('\n')
        self.assertEqual(3, len(printed_lines))

    def test_adjust_timing_yescurrent_zerodisplaced(self):
        self.journal.actions[0].dt -= datetime.timedelta(hours=1, minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(hours=1, minutes=10)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(hours=1, minutes=5)))
        self.input_values.append('1')
        self.input_values.append('2')
        self.input_values.append('1:03:00')
        self.input_values.append('y')
        self.journal.adjust_timing()
        self.assertTrue("Was unable" not in printed.getvalue())
        self.assertTrue("invalid" not in printed.getvalue())
        self.assertTrue("cancelled" not in printed.getvalue())
        self.assertEqual(68, self.journal.count_time_in_action(journal.TASK_SWITCH, 0)/60)
        self.assertEqual(journal.TASK_WALK, self.journal.actions[-1].action)

    def test_adjust_timing_nocurrent_onedisplaced(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.actions.append(journal.Action(action=journal.TASK_LUNCH, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=9)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=2)))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=2)))
        self.input_values.append('')
        self.input_values.append('4')
        self.input_values.append('-5:01')
        self.input_values.append('y')
        self.journal.adjust_timing()
        self.assertTrue("Was unable" not in printed.getvalue())
        self.assertTrue("invalid" not in printed.getvalue())
        self.assertTrue("cancelled" not in printed.getvalue())
        self.assertEqual(6, int(self.journal.count_time_in_action(journal.TASK_SWITCH, 0)/60))
        self.assertEqual(1, int(self.journal.count_time_in_action(journal.TASK_LUNCH, -1)/60))
        self.assertEqual(2, int(self.journal.count_time_in_action(journal.TASK_WALK, -1)/60))
        self.assertEqual(journal.TASK_WALK, self.journal.actions[-1].action)
        self.assertEqual(journal.TASK_WALK, self.journal.cur_action)
        self.assertEqual(-1, self.journal.cur_action_key)

    def test_adjust_timing_future_fail(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=2)))
        self.input_values.append('')        # How many
        self.input_values.append('2')       # Which
        self.input_values.append('10:00')   # By how much
        self.journal.adjust_timing()
        self.assertTrue("unable" not in printed.getvalue())
        self.assertTrue("future" in printed.getvalue())
        self.assertTrue("cancelled" in printed.getvalue())
        self.assertEqual(8, self.journal.count_time_in_action(journal.TASK_SWITCH, 0)/60)

    def test_adjust_timing_cancel_fail(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=2)))
        self.input_values.append('')        # How many
        self.input_values.append('2')       # Which
        self.input_values.append('3')       # By how much
        self.input_values.append('n')       # if you continue
        self.journal.adjust_timing()
        self.assertTrue("unable" not in printed.getvalue())
        self.assertTrue("cancelled" in printed.getvalue())
        self.assertEqual(8, self.journal.count_time_in_action(journal.TASK_SWITCH, 0)/60)

    def test_adjust_timing_invalid_time_fail(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.actions.append(journal.Action(action=journal.TASK_WALK, task_id=-1, dt=datetime.datetime.now() - datetime.timedelta(minutes=2)))
        self.input_values.append('')        # How many
        self.input_values.append('2')       # Which
        self.input_values.append('Hello World!')       # By how much
        self.input_values.append('n')       # if you continue 
        self.assertEqual(8, self.journal.count_time_in_action(journal.TASK_SWITCH, 0)/60)

    def test_complete_query_yesinans_beatestimation(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=15, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.cur_action = journal.TASK_SWITCH
        self.journal.cur_action_key = 0
        journal.complete_query(self.journal, "y")
        self.assertTrue("beat your estimation by 5 minutes" in printed.getvalue())
        self.assertTrue(self.journal.tasks[0].completed)

    def test_complete_query_yesinans_nobeatestimation(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10, seconds=5)
        self.journal.tasks.append(journal.Task(name='test_task', time=5, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10, seconds=5)))
        self.journal.cur_action = journal.TASK_SWITCH
        self.journal.cur_action_key = 0
        journal.complete_query(self.journal, "y")
        self.assertTrue("You took 5 minutes" in printed.getvalue())
        self.assertTrue(self.journal.tasks[0].completed)

    def test_complete_query_noinans(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.cur_action = journal.TASK_SWITCH
        self.journal.cur_action_key = 0
        journal.complete_query(self.journal, "n")
        self.assertFalse("beat your estimation by 9 minutes" in printed.getvalue())
        self.assertFalse(self.journal.tasks[0].completed)

    def test_complete_query_emptyans_invalchar(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        self.journal.actions.append(journal.Action(action=journal.TASK_SWITCH, task_id=0, dt=datetime.datetime.now() - datetime.timedelta(minutes=10)))
        self.journal.cur_action = journal.TASK_SWITCH
        self.journal.cur_action_key = 0
        self.input_values.append('Hello World!')
        journal.complete_query(self.journal, "")
        self.assertTrue("Operation aborted" in printed.getvalue())
        self.assertFalse(self.journal.tasks[0].completed)

    def test_switch_task_towork_allinans(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=False))
        journal.switch_task(self.journal, 'w0')
        self.assertEqual(journal.TASK_SWITCH, self.journal.cur_action)
        self.assertEqual(0, self.journal.cur_action_key)

    def test_switch_task_topers_pinans_wascompleted(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_PERS_TYPE, completed=True))
        self.input_values.append('0')       # What task
        self.input_values.append('y')       # change its status
        journal.switch_task(self.journal, 'p')
        self.assertFalse(self.journal.tasks[0].completed)
        self.assertEqual(journal.TASK_SWITCH, self.journal.cur_action)
        self.assertEqual(0, self.journal.cur_action_key)

    def test_switch_task_towork_wascompleted_nocomplete(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_WORK_TYPE, completed=True))
        self.input_values.append('w')       # (w)ork task
        self.input_values.append('0')       # What task
        self.input_values.append('n')       # change its status
        journal.switch_task(self.journal, '')
        self.assertEqual(journal.TASK_ADD_TASKS, self.journal.cur_action)
        self.assertEqual(-1, self.journal.cur_action_key)
        self.assertTrue(self.journal.tasks[0].completed)

    def test_switch_task_towalk_kinans(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_PERS_TYPE, completed=False))
        journal.switch_task(self.journal, 'k')
        self.assertEqual(journal.TASK_WALK, self.journal.cur_action)
        self.assertEqual(-1, self.journal.cur_action_key)

    def test_switch_task_tolunch_linans(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_PERS_TYPE, completed=False))
        journal.switch_task(self.journal, 'l')
        self.assertEqual(journal.TASK_LUNCH, self.journal.cur_action)
        self.assertEqual(-1, self.journal.cur_action_key)

    def test_switch_task_toaddtasks_ainans(self):
        self.journal.actions[0].dt -= datetime.timedelta(minutes=10)
        self.journal.tasks.append(journal.Task(name='test_task', time=10, task_type=journal.TASK_PERS_TYPE, completed=False))
        journal.switch_task(self.journal, 'a')
        self.assertEqual(journal.TASK_ADD_TASKS, self.journal.cur_action)
        self.assertEqual(-1, self.journal.cur_action_key)

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(JournalController))
unittest.TextTestRunner(verbosity=2).run(suite)

sys.stdout = saved
