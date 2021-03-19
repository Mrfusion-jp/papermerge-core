import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .query_set import QuerySet
from .condition import Condition
from .task import Task


class Monitor:
    """
    Monitors celery task states based on incoming events.

    papermerge.avenues is basically a django channels based app.

    Celery does not provide a convinient task monitoring API, it just
    blindly saves tasks' metadata.
    This class is ment to fill that gap. It conviniently saves
    events information and provides a handy API to work with
    saved tasks.

    Example of usage:

    monitor = Monitor(store=RedisStore())

    # Monitor celery task with specified name

    monitor.add_condition(
        name='papermerge.core.tasks.ocr_page',
        attr=[  # extract this kwargs from the task
            'user_id',
            'document_id',
            'lang'
        ]

    # Get a QuerySet for 'papermerge.core.tasks.ocr_page' tasks
    # so that saved tasks can queries in similar way to django models are
    ocr_page_qs = monitor['papermerge.core.tasks.ocr_page']

    # total count of ocr_page tasks
    ocr_page_qs.count()

    # total count of ocr_page tasks executed specifically for DOC_ID
    ocr_page_qs.find(document_id=DOC_ID).count()

    # iterage over all tasks for document ID which are still active
    # i.e. their stage is one of:
    # * task-sent
    # * task-received
    # * task-started
    for task in ocr_page_qs.find(document_id=DOC_ID).active():
        print(task['page_num'], task['state'])

    """

    def __init__(self, store, prefix="task-monitor"):
        # redis store
        self.store = store
        self.prefix = prefix
        self._conditions = []

    def add_condition(self, **kwargs):
        self._conditions.append(
            Condition(**kwargs)
        )

    def get_key(self, event):

        task_id = event['uuid']
        key = f"{self.prefix}-{task_id}"

        return key

    def extract_attr(self, event: dict, attrs: list) -> dict:
        ret = {}

        kwargs = event['kwargs']
        if len(kwargs) <= 2:
            return {}

        data = json.loads(kwargs.replace("'", '"'))
        for attr in attrs:
            ret[attr] = data.get(attr, '')

        return ret

    def save_event(self, event):

        task_dict = {}
        key = self.get_key(event)

        for condition in self._conditions:
            if condition != event.get('name', None):
                continue

            task_dict = self._extract_attr(event, condition.attrs)

        task = self._merge(key, task_dict)
        self._notify_avenues(task)

    def _merge(self, key, attr_dict):
        """
        Merge new attributes into existing task key
        """
        existing_task_dict = self._store[key]
        existing_task_dict.update(attr_dict)

        self.store[key] = existing_task_dict
        self.store.expire(key)

        return Task(**existing_task_dict)

    def __getitem__(self, task_name):
        """
        Returns an iterator over saved tasks with specified name
        """
        return QuerySet(task_name=task_name)

    def _notify_avenues(self, task):
        channel_layer = get_channel_layer()
        channel_data = task.to_dict()
        channel_data["type"] = f"ocr_page.{task.state}"

        async_to_sync(
            channel_layer.group_send
        )(
            "page_status", channel_data
        )
