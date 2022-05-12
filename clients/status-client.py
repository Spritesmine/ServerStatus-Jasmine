#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Update by: https://github.com/Spritesmine/ServerStatus-Jasmine
# 版本：1.0.3, 支持Python版本：2.7 to 3.9
# 支持操作系统： Linux, OSX, FreeBSD, OpenBSD and NetBSD, both 32-bit and 64-bit architectures
# 说明: 默认情况下修改server和user就可以了。丢包率监测方向可以自定义，例如：CU = "www.facebook.com"。

import socket
import time
import timeit
import re
import os
import sys
import json
import errno
import subprocess
from collections import deque
import threading
try:
    from queue import Queue     # python3
except ImportError:
    from Queue import Queue     # python2

SERVER = "127.0.0.1"
PORT = 35601
USER = "USER"
PASSWORD = "USER_PASSWORD"
CU = "cu.tz.cloudcpp.com" # 接口来自 tz.cloudcpp.com
CT = "ct.tz.cloudcpp.com" # 接口来自 tz.cloudcpp.com
CM = "cm.tz.cloudcpp.com" # 接口来自 tz.cloudcpp.com
PROBEPORT = 80
PROBE_PROTOCOL_PREFER = "ipv4"  # ipv4, ipv6
PING_PACKET_HISTORY_LEN = 100
INTERVAL = 1  # 更新间隔，单位：秒


def check_interface(net_name):
    net_name = net_name.strip()
    invalid_name = ['lo', 'tun', 'kube', 'docker', 'vmbr', 'br-', 'vnet', 'veth']
    return not any(name in net_name for name in invalid_name)


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime = f.readline().split('.')
    return int(uptime[0])


def get_memory():
    re_parser = re.compile(r'(\S*):\s*(\d*)\s*kB')
    result = dict()
    for line in open('/proc/meminfo'):
        match = re_parser.match(line)
        if match:
            result[match.group(1)] = int(match.group(2))

    mem_total = float(result['MemTotal'])
    mem_free = float(result['MemFree'])
    buffers = float(result['Buffers'])
    cached = float(result['Cached'])
    mem_used = mem_total - (mem_free + buffers + cached)
    swap_total = float(result['SwapTotal'])
    swap_free = float(result['SwapFree'])
    return int(mem_total), int(mem_used), int(swap_total), int(swap_free)


def get_hdd():
    p = subprocess.check_output(
        ['df', '-Tlm', '--total', '-t', 'ext4', '-t', 'ext3', '-t', 'ext2', '-t', 'reiserfs', '-t', 'jfs', '-t', 'ntfs',
         '-t', 'fat32', '-t', 'btrfs', '-t', 'fuseblk', '-t', 'zfs', '-t', 'simfs', '-t', 'xfs']).decode('utf-8')
    total = p.splitlines()[-1]
    used = total.split()[3]
    size = total.split()[2]
    return int(size), int(used)


def get_load():
    return round(os.getloadavg()[0], 1)


def get_cpu_time():
    with open('/proc/stat', 'r') as stat_file:
        time_list = stat_file.readline().split()[1:]
    time_list = list(map(int, time_list))
    return sum(time_list), time_list[3]


def get_cpu():
    old_total, old_idle = get_cpu_time()
    time.sleep(INTERVAL)
    total, idle = get_cpu_time()
    return round(100 - float(idle - old_idle) / (total - old_total) * 100.00, 1)


def get_traffic_vnstat():
    vnstat = os.popen('vnstat --oneline b').readline()
    if "Not enough data available yet" in vnstat:
        return 0, 0
    v_data = vnstat.split(';')
    net_in = int(v_data[8])
    net_out = int(v_data[9])
    return net_in, net_out


class Network:
    def __init__(self):
        self.rx = deque(maxlen=10)
        self.tx = deque(maxlen=10)
        self._get_traffic()

    def _get_traffic(self):
        net_in = 0
        net_out = 0
        re_parser = re.compile(r'([^\s]+):[\s]*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+('
                               r'\d+)\s+(\d+)\s+(\d+)')
        with open('/proc/net/dev') as f:
            for line in f.readlines():
                net_info = re_parser.findall(line)
                if net_info:
                    if check_interface(net_info[0][0]):
                        net_in += int(net_info[0][1])
                        net_out += int(net_info[0][9])
        self.rx.append(net_in)
        self.tx.append(net_out)

    def get_speed(self):
        self._get_traffic()
        avg_rx = 0
        avg_tx = 0
        queue_len = len(self.rx)
        for x in range(queue_len - 1):
            avg_rx += self.rx[x + 1] - self.rx[x]
            avg_tx += self.tx[x + 1] - self.tx[x]
        avg_rx = int(avg_rx / queue_len / INTERVAL)
        avg_tx = int(avg_tx / queue_len / INTERVAL)
        return avg_rx, avg_tx

    def get_traffic(self):
        queue_len = len(self.rx)
        return self.rx[queue_len - 1], self.tx[queue_len - 1]


def liuliang():
    NET_IN = 0
    NET_OUT = 0
    with open('/proc/net/dev') as f:
        for line in f.readlines():
            netinfo = re.findall('([^\s]+):[\s]{0,}(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
            if netinfo:
                if netinfo[0][0] == 'lo' or 'tun' in netinfo[0][0] \
                        or 'docker' in netinfo[0][0] or 'veth' in netinfo[0][0] \
                        or 'br-' in netinfo[0][0] or 'vmbr' in netinfo[0][0] \
                        or 'vnet' in netinfo[0][0] or 'kube' in netinfo[0][0] \
                        or netinfo[0][1]=='0' or netinfo[0][9]=='0':
                    continue
                else:
                    NET_IN += int(netinfo[0][1])
                    NET_OUT += int(netinfo[0][9])
    return NET_IN, NET_OUT

def tupd():
    '''
    tcp, udp, process, thread count: for view ddcc attack , then send warning
    :return:
    '''
    s = subprocess.check_output("ss -t|wc -l", shell=True)
    t = int(s[:-1])-1
    s = subprocess.check_output("ss -u|wc -l", shell=True)
    u = int(s[:-1])-1
    s = subprocess.check_output("ps -ef|wc -l", shell=True)
    p = int(s[:-1])-2
    s = subprocess.check_output("ps -eLf|wc -l", shell=True)
    d = int(s[:-1])-2
    return t,u,p,d


def get_network(ip_version):
    if ip_version == 4:
        host = 'ipv4.google.com'
    elif ip_version == 6:
        host = 'ipv6.google.com'
    else:
        return False
    try:
        socket.create_connection((host, 80), 2).close()
        return True
    except Exception:
        return False


lostRate = {
    '10010': 0.0,
    '189': 0.0,
    '10086': 0.0
}
pingTime = {
    '10010': 0,
    '189': 0,
    '10086': 0
}
netSpeed = {
    'netrx': 0.0,
    'nettx': 0.0,
    'clock': 0.0,
    'diff': 0.0,
    'avgrx': 0,
    'avgtx': 0
}
diskIO = {
    'read': 0,
    'write': 0
}

def _ping_thread(host, mark, port):
    lostPacket = 0
    packet_queue = Queue(maxsize=PING_PACKET_HISTORY_LEN)

    IP = host
    if host.count(':') < 1:     # if not plain ipv6 address, means ipv4 address or hostname
        try:
            if PROBE_PROTOCOL_PREFER == 'ipv4':
                IP = socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
            else:
                IP = socket.getaddrinfo(host, None, socket.AF_INET6)[0][4][0]
        except Exception:
                pass

    while True:
        if packet_queue.full():
            if packet_queue.get() == 0:
                lostPacket -= 1
        try:
            b = timeit.default_timer()
            socket.create_connection((IP, port), timeout=1).close()
            pingTime[mark] = int((timeit.default_timer() - b) * 1000)
            packet_queue.put(1)
        except socket.error as error:
            if error.errno == errno.ECONNREFUSED:
                pingTime[mark] = int((timeit.default_timer() - b) * 1000)
                packet_queue.put(1)
            #elif error.errno == errno.ETIMEDOUT:
            else:
                lostPacket += 1
                packet_queue.put(0)

        if packet_queue.qsize() > 30:
            lostRate[mark] = float(lostPacket) / packet_queue.qsize()

        time.sleep(INTERVAL)

def _net_speed():
    while True:
        with open("/proc/net/dev", "r") as f:
            net_dev = f.readlines()
            avgrx = 0
            avgtx = 0
            for dev in net_dev[2:]:
                dev = dev.split(':')
                if "lo" in dev[0] or "tun" in dev[0] \
                        or "docker" in dev[0] or "veth" in dev[0] \
                        or "br-" in dev[0] or "vmbr" in dev[0] \
                        or "vnet" in dev[0] or "kube" in dev[0]:
                    continue
                dev = dev[1].split()
                avgrx += int(dev[0])
                avgtx += int(dev[8])
            now_clock = time.time()
            netSpeed["diff"] = now_clock - netSpeed["clock"]
            netSpeed["clock"] = now_clock
            netSpeed["netrx"] = int((avgrx - netSpeed["avgrx"]) / netSpeed["diff"])
            netSpeed["nettx"] = int((avgtx - netSpeed["avgtx"]) / netSpeed["diff"])
            netSpeed["avgrx"] = avgrx
            netSpeed["avgtx"] = avgtx
        time.sleep(INTERVAL)

def _disk_io():
    '''
    good luck for opensource! by: cpp.la
    磁盘IO：因为IOPS原因，SSD和HDD、包括RAID卡，ZFS等阵列技术。IO对性能的影响还需要结合自身服务器情况来判断。
    比如我这里是机械硬盘，大量做随机小文件读写，那么很低的读写也就能造成硬盘长时间的等待。
    如果这里做连续性IO，那么普通机械硬盘写入到100Mb/s，那么也能造成硬盘长时间的等待。
    磁盘读写有误差：4k，8k ，https://stackoverflow.com/questions/34413926/psutil-vs-dd-monitoring-disk-i-o
    :return:
    '''
    while True:
        # pre pid snapshot
        snapshot_first = {}
        # next pid snapshot
        snapshot_second = {}
        # read count snapshot
        snapshot_read = 0
        # write count snapshot
        snapshot_write = 0
        # process snapshot
        pid_snapshot = [str(i) for i in os.listdir("/proc") if i.isdigit() is True]
        for pid in pid_snapshot:
            try:
                with open("/proc/{}/io".format(pid)) as f:
                    pid_io = {}
                    for line in f.readlines():
                        if "read_bytes" in line:
                            pid_io["read"] = int(line.split("read_bytes:")[-1].strip())
                        elif "write_bytes" in line and "cancelled_write_bytes" not in line:
                            pid_io["write"] = int(line.split("write_bytes:")[-1].strip())
                    pid_io["name"] = open("/proc/{}/comm".format(pid), "r").read().strip()
                    snapshot_first[pid] = pid_io
            except:
                if pid in snapshot_first:
                    snapshot_first.pop(pid)

        time.sleep(INTERVAL)

        for pid in pid_snapshot:
            try:
                with open("/proc/{}/io".format(pid)) as f:
                    pid_io = {}
                    for line in f.readlines():
                        if "read_bytes" in line:
                            pid_io["read"] = int(line.split("read_bytes:")[-1].strip())
                        elif "write_bytes" in line and "cancelled_write_bytes" not in line:
                            pid_io["write"] = int(line.split("write_bytes:")[-1].strip())
                    pid_io["name"] = open("/proc/{}/comm".format(pid), "r").read().strip()
                    snapshot_second[pid] = pid_io
            except:
                if pid in snapshot_first:
                    snapshot_first.pop(pid)
                if pid in snapshot_second:
                    snapshot_second.pop(pid)

        for k, v in snapshot_first.items():
            if snapshot_first[k]["name"] == snapshot_second[k]["name"] and snapshot_first[k]["name"] != "bash":
                snapshot_read += (snapshot_second[k]["read"] - snapshot_first[k]["read"])
                snapshot_write += (snapshot_second[k]["write"] - snapshot_first[k]["write"])
        diskIO["read"] = snapshot_read
        diskIO["write"] = snapshot_write

def get_realtime_data():
    '''
    real time get system data
    :return:
    '''
    t1 = threading.Thread(
        target=_ping_thread,
        kwargs={
            'host': CU,
            'mark': '10010',
            'port': PROBEPORT
        }
    )
    t2 = threading.Thread(
        target=_ping_thread,
        kwargs={
            'host': CT,
            'mark': '189',
            'port': PROBEPORT
        }
    )
    t3 = threading.Thread(
        target=_ping_thread,
        kwargs={
            'host': CM,
            'mark': '10086',
            'port': PROBEPORT
        }
    )
    t4 = threading.Thread(
        target=_net_speed,
    )
    t5 = threading.Thread(
        target=_disk_io,
    )
    for ti in [t1, t2, t3, t4, t5]:
        ti.setDaemon(True)
        ti.start()

def byte_str(object):
    '''
    bytes to str, str to bytes
    :param object:
    :return:
    '''
    if isinstance(object, str):
        return object.encode(encoding="utf-8")
    elif isinstance(object, bytes):
        return bytes.decode(object)
    else:
        print(type(object))



if __name__ == '__main__':
	for argc in sys.argv:
        if 'SERVER' in argc:
            SERVER = argc.split('SERVER=')[-1]
        elif 'PORT' in argc:
            PORT = int(argc.split('PORT=')[-1])
        elif 'USER' in argc:
            USER = argc.split('USER=')[-1]
        elif 'PASSWORD' in argc:
            PASSWORD = argc.split('PASSWORD=')[-1]
        elif 'INTERVAL' in argc:
            INTERVAL = int(argc.split('INTERVAL=')[-1])
    socket.setdefaulttimeout(30)
	get_realtime_data()
    while True:
        try:
            print('Connecting...')
            s = socket.create_connection((SERVER, PORT))
            data = s.recv(1024).decode()
            if data.find('Authentication required') > -1:
                s.send((USER + ':' + PASSWORD + '\n').encode('utf-8'))
                data = s.recv(1024).decode()
                if data.find('Authentication successful') < 0:
                    print(data)
                    raise socket.error
            else:
                print(data)
                raise socket.error

            print(data)
            if data.find('You are connecting via') < 0:
                data = s.recv(1024).decode()
                print(data)

            timer = 0
            check_ip = 0
            if data.find('IPv4') > -1:
                check_ip = 6
            elif data.find('IPv6') > -1:
                check_ip = 4
            else:
                print(data)
                raise socket.error

            traffic = Network()
            while True:
                CPU = get_cpu()
                NetRx, NetTx = traffic.get_speed()
                NET_IN, NET_OUT = traffic.get_traffic()
                Uptime = get_uptime()
                Load = get_load()
                MemoryTotal, MemoryUsed, SwapTotal, SwapFree = get_memory()
                HDDTotal, HDDUsed = get_hdd()

                array = {}
                if not timer:
                    array['online' + str(check_ip)] = get_network(check_ip)
                    timer = 150
                else:
                    timer -= 1 * INTERVAL

                array['uptime'] = Uptime
                array['load'] = Load
				array['load_1'] = Load_1
				array['load_5'] = Load_5
				array['load_15'] = Load_15
                array['memory_total'] = MemoryTotal
                array['memory_used'] = MemoryUsed
                array['swap_total'] = SwapTotal
                array['swap_used'] = SwapTotal - SwapFree
                array['hdd_total'] = HDDTotal
                array['hdd_used'] = HDDUsed
                array['cpu'] = CPU
                array['network_rx'] = NetRx
                array['network_tx'] = NetTx
                array['network_in'] = NET_IN
                array['network_out'] = NET_OUT
				# todo：兼容旧版本，下个版本删除ip_status
				array['ip_status'] = True
				array['ping_10010'] = lostRate.get('10010') * 100
				array['ping_189'] = lostRate.get('189') * 100
				array['ping_10086'] = lostRate.get('10086') * 100
				array['time_10010'] = pingTime.get('10010')
				array['time_189'] = pingTime.get('189')
				array['time_10086'] = pingTime.get('10086')
				array['tcp'], array['udp'], array['process'], array['thread'] = tupd()
				array['io_read'] = diskIO.get("read")
				array['io_write'] = diskIO.get("write")
				
                s.send(("update " + json.dumps(array) + '\n').encode('utf-8'))
        except KeyboardInterrupt:
            raise
        except socket.error:
            print('Disconnected...')
            # keep on trying after a disconnect
            if 's' in locals().keys():
                del s
            time.sleep(3)
        except Exception as e:
            print('Caught Exception:', e)
            if 's' in locals().keys():
                del s
            time.sleep(3)
