import time

from huey import RedisHuey, SqliteHuey, crontab
from fastapi import FastAPI
from huey.signals import SIGNAL_ERROR, SIGNAL_COMPLETE

huey = SqliteHuey('my-app')
app = FastAPI()

n = 1


# @huey.signal()
# def print_signal_args(signal, task, exc=None):
#     global n
#     if signal == SIGNAL_ERROR:
#         print('%s - %s - exception: %s' % (signal, task.id, exc))
#     else:
#         print(f'Hardloop: {n} --  {signal} - {task.id}')
#     if signal == SIGNAL_COMPLETE:
#         print(f"Task is complete.")

@huey.task()
def run_cplex_solver(value, write_out):
    time.sleep(1)
    print(f"Running CPLEX solver {write_out}")
    return write_out


@huey.task()
def do_excel_write_out(d):
    time.sleep(1)
    print("Updating Excel")
    d['write_out'] = d['value'] + d['value']
    print(d)
    return dict(d)


@app.get("/")
def home():
    global n
    n += 1
    my_dict = {"value": n}
    excel = do_excel_write_out.s(my_dict)
    pipeline = excel.then(run_cplex_solver)
    result_group = huey.enqueue(pipeline)
    return "Done"
