# Common function 
# print function 
#

def writeDataToFile(f_name,str_to_write):
        try:
                f = open(f_name, 'r+')
        except IOError as e:
                print f_name, '  Created '
                f=open(f_name,'w+')

        f.read()
        pos = f.tell()
        f.seek(pos)
        string = ('[INFO][%s]  ' % time.ctime() + str_to_write + '\n')
        f.write(string)
        f.close()

def print_time(threadName, delay):
        count = 5
        while count:
                time.sleep(delay)
                print threadName, ' time : ',time.strftime('%H:%M:%S')
                count -= 1
