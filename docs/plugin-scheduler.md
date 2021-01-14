# plugin scheduler

The installed plugins in supervisor are CPU and memory resources.
We want to remove unused plugins as soon as possible.

We detects the last call of get_plugin_endpoint is greater than 2 days. We assume that this plugin is not used.

# Configuration

Create plugin scheduler service

* configure QUEUES
* configure SCHEDULERS
* configure WORKERS

~~~
      QUEUES:
        plugin_cleanup_q:
          backend: spaceone.core.queue.redis_queue.RedisQueue
          host: redis
          port: 6379
          channel: plugin_cleanup_q

      SCHEDULERS:
        cleanup_scheduler:
          backend: spaceone.plugin.scheduler.cleanup_scheduler.CleanupScheduler
          queue: plugin_cleanup_q
          interval: 24
          minute: ':30'

      WORKERS:
        cleanup_worker:
          backend: spaceone.core.scheduler.worker.BaseWorker
          queue: plugin_cleanup_q
          pool: 1
~~~

