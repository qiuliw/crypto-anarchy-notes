import multiprocessing
from producer import producer
from consumer import consumer
from time import sleep

# Make sure that a RabbitMQ server is running, or otherwise
# this program will fail.

if __name__ == "__main__":
	p = multiprocessing.Process(target=producer)
	c = multiprocessing.Process(target=consumer)

	p.start()
	sleep(2)
	c.start()

	p.join()
	c.join()
	
