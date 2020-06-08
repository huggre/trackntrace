from redis import Redis
import rq
queue = rq.Queue('default', connection=Redis.from_url('redis://'))
job = queue.enqueue('tasks.example', 23)
jid = job.get_id()
print(jid)
