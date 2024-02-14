import MQTTclient

from queue import Queue
from threading import Thread

class Program:

    def __init__(self, sub_config, pub_configs, topic_dispatcher):

        self.queue = Queue()

        self.sub_config = sub_config
        self.pub_configs = pub_configs
        self.topic_dispatcher = topic_dispatcher

        self.subscriber = None
        self.publisher = []

        self.init_subscriber()
        self.init_publisher()

        processor_thread = Thread(target=self.message_processor)
        processor_thread.start()
    
    def init_subscriber(self):
        self.subscriber = MQTTclient.Subscriber(config=self.sub_config, queue=self.queue)

    def init_publisher(self):
        for config in self.pub_configs:
            self.publisher.append(MQTTclient.Publisher(config=config))

    def message_processor(self):
        while True:
            # Blocking call, no CPU waste here
            message = self.queue.get()  
            if message:
                callback = self.topic_dispatcher.get(message.topic, self.handle_unknown_topic)
                callback_thread = Thread(target=callback, args=(message.topic, message.payload.decode('utf8'), self.publisher, ))
                callback_thread.start()

    def handle_unknown_topic(self, topic, data, publisher):
        # 알 수 없는 토픽 처리 로직
        print(f"Received message from unknown topic {topic}: {data}")

    
    def start(self):
        pass

        
    