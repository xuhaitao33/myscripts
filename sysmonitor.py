# Importing the required libraries
import psutil
import time
import sys
import signal
import os
import re
import socket

import matplotlib.pyplot as plt

hostname = socket.gethostname()
ip_addresses = socket.getaddrinfo(hostname, None, socket.AF_INET6)
ip_address = ip_addresses[0][4][0]

total_time=float(sys.argv[2])
gap_time=float(sys.argv[1])

cpu_file='./cpu.txt'
mem_file='./mem.txt'
net_file='./net.txt'

def draw_cpu(path):
    global x_start
    global x_end
    nodes_x={}
    nodes_y={}
    with open(path) as f_read:
        data = f_read.read()
    re_find = re.findall('([0-9a-z:\.]{1,}) (\d+\.\d+) (\d+\.\d+)', data)
    for line in re_find:
        node=line[0]
        if node not in nodes_x:
            nodes_x[node]=[]
            nodes_y[node]=[]
        nodes_x[node].append(float(line[1]))
        nodes_y[node].append(float(line[2]))

    for node in nodes_x:
        x_start = min(nodes_x[node][0]-1, x_start)
        x_end = max(nodes_x[node][len(nodes_x[node])-1]+1, x_end)
        plt.plot(nodes_x[node], nodes_y[node], label=node+" cpu", marker='o', markersize=2)

def draw_mem(path):
    global x_start
    global x_end
    nodes_x={}
    nodes_y={}
    with open(path) as f_read:
        data = f_read.read()
    re_find = re.findall('([0-9a-z:\.]{1,}) (\d+\.\d+) (\d+)', data)
    for line in re_find:
        node=line[0]
        if node not in nodes_x:
            nodes_x[node]=[]
            nodes_y[node]=[]
        nodes_x[node].append(float(line[1]))
        nodes_y[node].append(float(line[2]))

    for node in nodes_x:
        plt.plot(nodes_x[node], nodes_y[node], label=node+" mem")

def draw_net_send(path):
    nodes_x={}
    nodes_y={}
    with open(path) as f_read:
        data = f_read.read()
    re_find = re.findall('([0-9a-z:\.]{1,}) (\d+\.\d+) (\d+)', data)
    x=[]
    y=[]
    for line in re_find:
        node=line[0]
        if node not in nodes_x:
            nodes_x[node]=[]
            nodes_y[node]=[]
        nodes_x[node].append(float(line[1]))
        nodes_y[node].append(float(line[2]))

    for node in nodes_x:
        plt.plot(nodes_x[node], nodes_y[node], label=node+" send")

def draw_net_recv(path):
    nodes_x={}
    nodes_y={}
    with open(path) as f_read:
        data = f_read.read()
    re_find = re.findall('([0-9a-z:\.]{1,}) (\d+\.\d+) (\d+) (\d+)', data)
    x=[]
    y=[]
    for line in re_find:
        node=line[0]
        if node not in nodes_x:
            nodes_x[node]=[]
            nodes_y[node]=[]
        nodes_x[node].append(float(line[1]))
        nodes_y[node].append(float(line[3]))

    for node in nodes_x:
        plt.plot(nodes_x[node], nodes_y[node], label=node+" recv")

cpu_fp=open(cpu_file,'w')
mem_fp=open(mem_file,'w')
net_fp=open(net_file,'w')

last_net_io_counters_ = psutil.net_io_counters()

# Creating an almost infinite for loop to monitor the details continuously
for i in range(int(total_time/gap_time)):
    try:
        cpu_usage = psutil.cpu_percent()
        print(time.time(), cpu_usage)
        cpu_fp.write('{} {} {}\n'.format(ip_address, time.time(), cpu_usage))

        mem_usage = psutil.virtual_memory().percent
        mem_fp.write('{} {} {}\n'.format(ip_address, time.time(), mem_usage))
        print(time.time(), mem_usage)

        net_io_counters_ = psutil.net_io_counters()
        print(
            time.time(),
            net_io_counters_.bytes_sent-last_net_io_counters_.bytes_sent,
            net_io_counters_.bytes_recv-last_net_io_counters_.bytes_recv,
            net_io_counters_.packets_sent-last_net_io_counters_.packets_sent,
            net_io_counters_.packets_recv-last_net_io_counters_.packets_recv
        )
        net_fp.write('{} {} {} {} {} {}\n'.format(
            ip_address,
            time.time(),
            net_io_counters_.bytes_sent-last_net_io_counters_.bytes_sent,
            net_io_counters_.bytes_recv-last_net_io_counters_.bytes_recv,
            net_io_counters_.packets_sent-last_net_io_counters_.packets_sent,
            net_io_counters_.packets_recv-last_net_io_counters_.packets_recv
        ))
        last_net_io_counters_ = net_io_counters_

        time.sleep(gap_time)
    except KeyboardInterrupt:
        sys.stderr.write("receive SIGINT\n")
        break

cpu_fp.close()
mem_fp.close()
net_fp.close()

x_start = 100000000000
x_end = 0

plt.figure(figsize=(20,20))

fig = plt.subplot(4,1,1)
plt.xlabel("timestamp")
plt.ylabel("%")
plt.title("cpu")
draw_cpu(cpu_file)
plt.grid()
plt.legend()
fig.set_xlim(x_start, x_end)
#plt.xticks([1, 2, 3, 4, 5])

fig = plt.subplot(4,1,2)
plt.xlabel("timestamp")
plt.ylabel("bytes")
plt.title("mem")
draw_mem(mem_file)
plt.grid()
plt.legend()
fig.set_xlim(x_start, x_end)

fig = plt.subplot(4,1,3)
plt.xlabel("timestamp")
plt.ylabel("bytes")
plt.title("net")
draw_net_send(net_file)
plt.grid()
plt.legend()
fig.set_xlim(x_start, x_end)

fig = plt.subplot(4,1,4)
plt.xlabel("timestamp")
plt.ylabel("bytes")
plt.title("net")
draw_net_recv(net_file)
plt.grid()
plt.legend()
fig.set_xlim(x_start, x_end)

# plt.show()
plt.gcf().savefig("monitor.png")
