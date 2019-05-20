from subprocess import check_output
import re
import matplotlib.pyplot as plt
import csv
import pandas
import os
import time
def median_time_regex(input):
    input = str(input)
    regex_90_percent = "(?:90%)(\s*[\d]*)"
    regex_50_percent = "(?:50%)(\s*[\d]*)"
    ninety = re.search(regex_90_percent, input).group(1)
    median = re.search(regex_50_percent, input).group(1)
    return int(median)/1000, int(ninety)/1000, 0


def testport(address, port, numRequests):
    timeout = 2000
    command = f"ab -n {numRequests} -c {numRequests} -s {timeout} -q -r {address}:{port}/ping"
    print(command)
    time_taken = check_output(command, shell = True)
    median_time, max_time, min_time  = median_time_regex(time_taken)
    return median_time, max_time, min_time

def compare(filename, address):
    file = open(filename, "w+")
    c = csv.writer(file)
    c.writerow(["number_of_requests", "Go_median_time","Go_max", "Go_max_error","Go_min", "Go_min_error", "Java_median_time", "Java_max", "Java_max_error","Java_min", "Java_min_error"])
    request_range = range(10, 50, 10)
    for num in request_range:
        go_median, go_max, go_min = testport(address, 9090, num)
        go_min_error = go_median - go_min
        go_max_error = go_max - go_median
        java_median, java_max, java_min = testport(address, 8080, num)
        java_min_error = java_median - java_min
        java_max_error = java_max - java_median
        c.writerow([num, go_median, go_max, go_max_error, go_min, go_min_error, java_median, java_max, java_max_error, java_min, java_min_error])
    file.close()

def generate_graph(filename):
    header = ["number_of_requests", "Go_median_time","Go_max", "Go_max_error","Go_min", "Go_min_error", "Java_median_time", "Java_max", "Java_max_error","Java_min", "Java_min_error"]
    data = pandas.read_csv(filename, names=header, skiprows = 1)
    plt.figure(figsize=(10,6))
    plt.plot(data.number_of_requests.tolist(), data.Java_median_time.tolist(), "o", label = "Java server", color='#ff9721')
    plt.plot(data.number_of_requests.tolist(), data.Java_max.tolist(), "^", label = "Java 90th percentile", color='#ff9721')

    plt.plot(data.number_of_requests.tolist(), data.Go_median_time.tolist(), "o", label = "Go server", color = '#4f92ff')
    plt.plot(data.number_of_requests.tolist(), data.Go_max.tolist(), "^", label = "Go 90th percentile", color = '#4f92ff')

    bottom, top = plt.ylim()
    # plt.ylim(top = top + 20)
    plt.title('Java vs Go server response time')
    plt.xlabel('Number of concurrent requests')
    plt.ylabel('Time taken (s)')
    plt.legend()
    # plt.xticks(ticks = [x for x in range(1000, 21000, 2000)],rotation=0)
    plt.savefig(os.path.abspath('..')+"/content/_img/JavaVsGoLoadTest.png", dpi=300, bbox_inches='tight', figsize=(50,25))
filename = "responsetime.csv"
address = "localhost"
if os.path.isfile(filename) is False:
    # try:
    #     print("pinging go server")
    #
    #     go_status = check_output("curl localhost:9090/ping", shell= True)
    #     print("successful")
    #
    # except:
        # print("starting go server")
    os.system("go run go/main.go > /dev/null &")
        # time.sleep(10)
    # try:
    #     print("pinging java server")
    #
    #     java_status = check_output("curl localhost:8080/ping", shell= True)
    #     print("successful")
    #
    # except:
    #     # os.system("cd java")
        # print("starting Java server")
    os.system("cd java && ./gradlew clean bootRun > /dev/null &")
    time.sleep(10) # wait for the server to start
    compare(filename, address)
    # If Responsetime doesn't exist, create is, otherwise just use what's already there


generate_graph(filename)
