'''
    Student:    Patrick Abejar
    Instructor: Professor Ledonwong
    Class:      IS 211 - Assignment 5
    Date:       5 October 2015
'''

import csv, argparse

''' Queque class implementation was retrieved from textbook '''
class Queue:
    def __init__(self):
        self.items = []
    def is_empty(self):
        return self.items == []
    def enqueue(self, item):
        self.items.insert(0,item)
    def dequeue(self):
        return self.items.pop()
    def size(self):
        return len(self.items)

''' Server class is a modified implementation of the Printer class from the textbook '''
class Server:
    def __init__(self):
        self.current_task = None
        self.time_remaining = 0
    def busy(self):
        if self.current_task != None:
            return True
        else:
            return False
    def startNext(self, new_request):
        self.current_task = new_request
        self.time_remaining = new_request.get_timeRequired()
    # This is used for decreasing the time required (left) by 1, which will be used for each passing second
    def decrementTimeRemaining(self):
        if ( self.time_remaining == 1 ):
            self.time_remaining = 0
            self.current_task = None
        else:
            self.time_remaining = self.time_remaining-1

''' Request class is a modified implementation of the Task class from the textbook '''
class Request:
    def __init__(self, timeIn, name, timeRequired):
        self.timeIn = timeIn
        self.name = name
        self.timeRequired = timeRequired
    def get_timeIn(self):
        return self.timeIn
    def get_name(self):
        return self.name
    def get_timeRequired(self):
        return self.timeRequired
    def wait_time(self, current_time):
        return current_time - self.timeIn

''' Contains the most of the simulation for only one server processing requests. It
    does this by constantly looping in a large while loop, each and every second of
    the simulation, feeding in requests to the queue based on information stated in
    the imported csv data file. The time that the request leaves the queue and enters
    the server is stored and the entrance time is subtracted to get the wait time.
    These wait times are later placed in a list for an average wait time calculation
    being performed. Servers can only handle one request at a time.
'''
def simulateOneServer(listedData):
    server = Server()        # Server object to process requests
    request_queue = Queue()  # Queue of requests
    waiting_times = []       # Record values for waiting time so that an average may be calculated later

    current_second = 0       # Keeps track of present second
    listedDataIndex = 0      # Used as a data index to load the parameter data

    # Keep continuing if the current second is not more than the last request's second on the loaded data from csv file
    # OR keep continuing if outside this range but there are still requests in the queue
    while ((current_second <= listedData[len(listedData)-1].get_timeIn()) or ((current_second > listedData[len(listedData)-1].get_timeIn()) and (not request_queue.is_empty())) ):

        # Checking that listedDataIndex does not take listedData out of bounds.
        if ( listedDataIndex < len(listedData)):

            # REQUEST --> QUEUE. Adding requests to the queue for each request that matches the TimeIn to the current_second
            while ( current_second == listedData[listedDataIndex].get_timeIn() ):
                request = Request(listedData[listedDataIndex].get_timeIn(), listedData[listedDataIndex].get_name(), listedData[listedDataIndex].get_timeRequired())
                request_queue.enqueue(request)
                listedDataIndex += 1

                # Once bounds reached on the list, there is no more data. This exits the while loop.
                if ( listedDataIndex == len(listedData) ):
                    break


        # SERVER --> SERVER. Server is busy processing any requests at the moment.
        if ( server.busy() ):
            server.decrementTimeRemaining()


        # QUEUE -- > SERVER. Adding queue requests to the server when server is not busy. Follows the First In First Out model.
        if ( (not request_queue.is_empty()) and (not server.busy())):
            next_request = request_queue.dequeue()
            waiting_times.append(next_request.wait_time(current_second))
            server.startNext(next_request)

        # Increment to the next second in time.
        current_second += 1

    # Calculation and printing of averages.
    average_wait = sum(waiting_times) / len(waiting_times)
    #print waiting_times
    print("Average Wait %6.2f secs." %(average_wait))

''' Contains the most of the simulation for multiple server processing requests. It
    does this by constantly looping in a large while loop, each and every second of
    the simulation, feeding in requests to the queue based on information stated in
    the imported csv data file. The time that the request leaves the queue and enters
    the server is stored and the entrance time is subtracted to get the wait time.
    These wait times are later placed in a list for an average wait time calculation
    being performed. Servers can only handle one request at a time, however there can
    be many servers processing the requests all in the same second.
'''
def simulateManyServers(listedData, numberOfServers):

    # Instantiate server and queue objects and contain them within a list dependent on the number the user inputs
    serverList = [None]*numberOfServers
    for x in range(0, numberOfServers):
        serverList[x] = (Server(), Queue())

    waiting_times = []       # Record values for waiting time so that an average may be calculated later

    current_second = 0       # Keeps track of present second
    listedDataIndex = 0      # Used as a data index to load the parameter data


    # Infinite loop with each cycle representing one second observed; breaks from the loop come later
    while ( True ):
        # Checking that listedDataIndex does not take listedData out of bounds.
        if ( listedDataIndex < len(listedData)):

            whoseTurn_Server = 0    # Kept track of which server is the one currenty allowed to operate based on
                                    # Round Robin

            # REQUEST --> QUEUE. Adding requests to the queue for each request that matches the TimeIn to the current_second
            while ( current_second == listedData[listedDataIndex].get_timeIn() ):
                request = Request(listedData[listedDataIndex].get_timeIn(), listedData[listedDataIndex].get_name(), listedData[listedDataIndex].get_timeRequired())
                serverList[whoseTurn_Server][1].enqueue(request)
                whoseTurn_Server += 1
                listedDataIndex += 1

                if (whoseTurn_Server >= numberOfServers):
                    whoseTurn_Server = 0

                # Once bounds reached on the list, there is no more data. This exits the while loop.
                if ( listedDataIndex == len(listedData) ):
                    break


        # SERVER --> SERVER. Server is busy processing any requests at the moment.
        for j in range(0, numberOfServers):
            if ( serverList[j][0].busy() ):
                serverList[j][0].decrementTimeRemaining()


        # QUEUE -- > SERVER. Adding queue requests to the server when server is not busy. Follows the First In First Out model.
        for a in range(0, numberOfServers):
            if ( (not serverList[a][1].is_empty()) and (not serverList[a][0].busy())):
                next_request = serverList[a][1].dequeue()
                waiting_times.append(next_request.wait_time(current_second))
                serverList[a][0].startNext(next_request)


        # Checks if any queue has an object
        allQueuesEmpty = None
        for z in range(0, numberOfServers):
            if ( not serverList[z][1].is_empty() ):
                allQueuesEmpty = False
                break
            allQueuesEmpty = True

        # Increment to the next second in time.
        current_second += 1

        # Once all queues have cleared out, one does not need to observe anymore proceeding seconds (time) so
        # a break is present here
        if ( allQueuesEmpty  and current_second > listedData[len(listedData)-1].get_timeIn()):
            break

    # Calculation and printing of averages.
    average_wait = sum(waiting_times) / len(waiting_times)
    # Print waiting_times
    print("Average Wait %6.2f secs." %(average_wait))


def main():

    data = None

    # Pass in an argument through the command prompt for file path of csv file
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Read a file of requests at this location")
    parser.add_argument("--servers", help="Indicate the amount of servers processing requests.")
    args = parser.parse_args()

    # Make sure file path is inputted
    if args.file == None:
        print "File path is required. Program exiting."
        exit()
    else:
        f = open(args.file, 'rt')
        reader = None
        try:
            reader = csv.reader(f)
        finally:
            None

        loadData = []

        # Loading data from the file to a list in the form of Request objects
        for row in reader:
            loadData.append(Request(int(row[0]), row[1], int(row[2])))

        try:
            if ( args.servers == None or int(args.servers) == 1 ):  # Servers is an optional arg which triggers 1 server
                simulateOneServer(loadData)
            elif ( int(args.servers) < 1 ):                         # Must be a positive integer amount
                print("You need to have at least one server. Program exiting.")
                exit()
            elif ( int(args.servers) > 1):
                simulateManyServers(loadData, int(args.servers))    # For multiple servers
        except Exception:
            print "Please enter an integer."

main()

'''
Question:   After running both simulations, what are the results do you see? How does each simulation differ in its
            average latency?
Answer:     The lesser amount of servers, the slower and longer the wait. Adding more and more servers cuts down the
            average latency wait time but it does not cut it in half when one doubles the servers present. Instead,
            it seems that after the single digit amount of servers, the wait time approaches one specific number, and
            in this case it approaches 1048 seconds despite the number of servers one adds after this threshold of 6
            servers. (One server runs at 4999 seconds for the average wait time.) This is all based on the posted
            requests.csv file from Blackboard.
'''