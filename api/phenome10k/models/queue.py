from sqlalchemy.sql import func

from phenome10k.extensions import db


class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(255))
    arguments = db.Column(db.JSON)
    created = db.Column(db.DateTime(), server_default=func.now())

    @staticmethod
    def add(method, *args):
        q = Queue(method=method, arguments=args)
        db.session.add(q)
        db.session.commit()

    @staticmethod
    def get():
        task = Queue.query.order_by('created').first()
        if task is None:
            return None

        method = task.method
        args = task.arguments

        db.session.delete(task)
        db.session.commit()

        return method, args

    @staticmethod
    def read(sleep=1):
        import time
        while True:
            task = Queue.get()
            if task is None:
                time.sleep(sleep)
            else:
                yield task
