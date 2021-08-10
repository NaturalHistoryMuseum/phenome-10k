from task_queue.apium import app


@app.task
def add(x, y):
    return x + y
