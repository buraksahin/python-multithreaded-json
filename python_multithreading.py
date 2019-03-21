"""
Python Multi Threading
JSON Handler
"""
import sys
import requests
import json
import random
import string
from threading import Thread
from queue import Queue
import time

# Variables
threadCount = 5
totalData = 128
totalCustomer = 100
totalPost = 5
# Customer address - GET
customerAddress = 'http://xxx.xxx.xxx.xxx/api/get-customer-list'
# Post address - GET
postAddress = 'http://xxx.xxx.xxx.xxx/api/get-post-list'
# Comment post address - POST
postUrl = 'http://xxx.xxx.xxx.xxx/api/add-comment'

##
# Handle JSON Works
##
class HandleJSON():
    ##
    # Initialize HandleJSON object
    ##
    def __init__(self):
        # Log
        print("JSON Handler has been initialized..")

    ##
    # Prepare JSON Data
    # param:(int)dataCount - Count of the total generated data
    # param:(int)customerCoun - Count of the total selected customer
    # param:(int)postCount - Count of the selected post
    # return:(list)preparedData - List of dictionary [JSON post data]
    ##
    # This method generate a list of dict as much as parameter of dataCount value
    # randomly prepare a post list, a customer can post multiple times
    ##
    # Also these count parameters can be using as range in different method
    # or we can get a customer list
    ##
    def prepareData(self, dataCount, customerCount, postCount):
        # Customer list
        customerData = requests.get(customerAddress).text
        # Post ID, We will get post id
        postData = requests.get(postAddress).text

        # Convert to JSON
        customerJSON = json.loads(customerData)
        postJSON = json.loads(postData)

        # Set minimum values
        lenCustomerList = len(customerJSON)
        lenPostJSON = len(postJSON)
        minCustomer = min(customerCount, lenCustomerList)
        minPostCount = min(postCount, lenPostJSON)

        # JSON Post Data
        preparedData = []
        while dataCount > 0:
            tokenData = customerJSON[dataCount % minCustomer]["token"]
            postIdData = int(postJSON[dataCount % minPostCount]["id"])
            randomComment = self.generateRandomComment()
            realName = 'Burak Sahin'
            postData = {
                'token': tokenData,
                'postId': postIdData,
                'comment': randomComment,
                'name': realName
            }
            preparedData.append(postData)
            dataCount -= 1
        return preparedData

    ##
    # Generate random comment
    ##
    def generateRandomComment(self):
        comment = ''.join([random.choice(string.ascii_uppercase + string.digits)
                           for _ in range(random.randint(5, 100))])
        return comment

##
# Thread Handler
##
class ThreadHandler(Thread):
    def __init__(self, workQueue):
        Thread.__init__(self)
        self.workQueue = workQueue
        print("Thread initializing..\n")

    def run(self):
        while True:
            try:
                postData = self.workQueue.get()
                posting = requests.post(postUrl, postData)
                postResponse = posting.text  # Post response
                print(postResponse, "\n")  # Print post response
            except Exception as e:
                print(e, "\n")  # Debug
            finally:
                self.workQueue.task_done()

##
# Main Class
##
class Main():
    def __init__(self):
        self.start()

    def start(self):
        # JSON Handler - this object will prepare json data
        jHandle = HandleJSON()

        # Prepare data
        preparedData = jHandle.prepareData(totalData, totalCustomer, totalPost)

        """
        # Show prepared data
        for t in range(totalData):
            print(preparedData[t])
        """

        # Create work queue
        workQueue = Queue()

        # Create threads
        threads = []
        for i in range(threadCount):
            t = ThreadHandler(workQueue)
            t.daemon = True
            t.start()
            threads.append(t)

        # Put works to queue
        for data in preparedData:
            workQueue.put(data)

        # Terminate
        workQueue.join()

"""
Create Main Object
"""
startTime = time.time()
m = Main()
elapsedTime = time.time() - startTime
print("Time has been elapsed: ", elapsedTime)
i = input("Press a key for exit..")
