import datetime
import sys
import threading
import time


class ClockThread (threading.Thread):
    def __init__(self, threadID,time_str,function ,*args):
        threading.Thread.__init__(self)
        self.clock = Clock(function,*args)
        self.time_list = time_str.split(':')
        if len(self.time_list) != 3:
            print 'Wrong Time List ...'
            sys.exit()
        self.clock.set_alarm(self.time_list[0], self.time_list[1], self.time_list[2])
        self.threadID = threadID
        self.args = tuple(i for i in args)


    def run(self):
        print "Alarm Set  "
        self.clock.run()



class Clock:

    def __init__(self, function, *args):
        self.alarm_time = None
        self._alarm_thread = None
        self.update_interval = 1
        self.event = threading.Event()
        self.function = function
        self.args = tuple(i for i in args)
        self.start = 1

    def run(self):
        while True:
            self.event.wait(self.update_interval)
            if self.event.isSet():
                break
            now = datetime.datetime.now()
            if self._alarm_thread and self._alarm_thread.is_alive():
                alarm_symbol = '+'
            else:
                alarm_symbol = ' '
            sys.stdout.write("\r%02d:%02d:%02d %s"
                % (now.hour, now.minute, now.second, alarm_symbol))
            sys.stdout.flush()

    def set_alarm(self, hour, minute, sec):
        now = datetime.datetime.now()
        alarm = now.replace(hour=int(hour), minute=int(minute), second=int(sec))
        delta = int((alarm - now).total_seconds())
        if delta <= 0:
            alarm = alarm.replace(day=alarm.day + 1)
            delta = int((alarm - now).total_seconds())

        print 'Rest time ' + str(datetime.timedelta(seconds=delta))
        if self.start == 0:
            self.function(*self.args)
        self.start = 0
        self._alarm_thread = threading.Timer(delta, self.set_alarm, [hour,minute,sec])
        self._alarm_thread.daemon = True
        self._alarm_thread.start()


if __name__ == '__main__':
    def function(a):
        print 'hello %s' % a

    t1 = ClockThread(1,'09:30:00',function,'fuck you man ~~~')
    t1.start()

    while True:
        print 'main alive'
        time.sleep(3600)
        #now = datetime.datetime.now()
        #sys.stdout.write('\r%02d:%02d:%02d' % (now.hour, now.minute, now.second))
        #sys.stdout.flush()
        pass