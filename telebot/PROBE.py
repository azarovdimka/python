from multiprocessing import Process, Queue
import time


def do_work(start, end, result):
    sum = 0
    for i in range(start, end):
        sum += i
    result.put(sum)
    return


s_time = time.time()
if __name__ == '__main__':
    START, END = 0, 80000000
    result = Queue()
    pr1 = Process(target=do_work, args=(START, int(END / 2), result))
    pr2 = Process(target=do_work, args=(int(END / 2), END, result))
    pr1.start()
    pr2.start()
    pr1.join()
    pr2.join()
    result.put('STOP')
    sum = 0
    while True:
        tmp = result.get()
        if tmp == 'STOP':
            break
        else:
            sum += tmp
print('Result : ', sum, 'time =', time.time() - s_time)
