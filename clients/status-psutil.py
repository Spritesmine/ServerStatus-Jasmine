#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Update by: https://github.com/Spritesmine/ServerStatus-Jasmine
# 依赖于psutil跨平台库：
# 版本：1.0.3, 支持Python版本：2.7 to 3.9
# 支持操作系统： Linux, Windows, OSX, Sun Solaris, FreeBSD, OpenBSD and NetBSD, both 32-bit and 64-bit architectures
# 说明: 默认情况下修改server和user就可以了。丢包率监测方向可以自定义，例如：CU = "www.facebook.com"。

import socket
import time
import timeit
import os
import sys
import json
import errno
import psutil
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
    return int(time.time() - psutil.boot_time())


def get_memory():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return int(mem.total / 1024.0), int(mem.used / 1024.0), int(swap.total / 1024.0), int(swap.used / 1024.0)


def get_hdd():
    valid_fs = ['ext4', 'ext3', 'ext2', 'reiserfs', 'jfs', 'btrfs', 'fuseblk', 'zfs', 'simfs', 'ntfs', 'fat32', 'exfat',
                'xfs']
    disks = dict()
    size = 0
    used = 0
    for disk in psutil.disk_partitions():
        if disk.device not in disks and disk.fstype.lower() in valid_fs:
            disks[disk.device] = disk.mountpoint
    for disk in disks.values():
        usage = psutil.disk_usage(disk)
        size += usage.total
        used += usage.used
    return int(size / 1024.0 / 1024.0), int(used / 1024.0 / 1024.0)


def get_load():
    try:
        return round(psutil.getloadavg()[0], 1)
    except Exception:
        return -1.0


def get_cpu():
    return psutil.cpu_percent(interval=INTERVAL)


class Network:
    def __init__(self):
        self.rx = deque(maxlen=10)
        self.tx = deque(maxlen=10)
        self._get_traffic()

    def _get_traffic(self):
        net_in = 0
        net_out = 0
        net = psutil.net_io_counters(pernic=True)
        for k, v in net.items():
            if check_interface(k):
                net_in += v[1]
                net_out += v[0]
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
    net = psutil.net_io_counters(pernic=True)
    for k, v in net.items():
        if 'lo' in k or 'tun' in k \
                or 'docker' in k or 'veth' in k \
                or 'br-' in k or 'vmbr' in k \
                or 'vnet' in k or 'kube' in k:
            continue
        else:
            NET_IN += v[1]
            NET_OUT += v[0]
    return NET_IN, NET_OUT

def tupd():
    '''
    tcp, udp, process, thread count: for view ddcc attack , then send warning
    :return:
    '''
    try:
        if sys.platform.startswith("linux") is True:
            t = int(os.popen('ss -t|wc -l').read()[:-1])-1
            u = int(os.popen('ss -u|wc -l').read()[:-1])-1
            p = int(os.popen('ps -ef|wc -l').read()[:-1])-2
            d = int(os.popen('ps -eLf|wc -l').read()[:-1])-2
        elif sys.platform.startswith("win") is True:
            t = int(os.popen('netstat -an|find "TCP" /c').read()[:-1])-1
            u = int(os.popen('netstat -an|find "UDP" /c').read()[:-1])-1
            p = len(psutil.pids())
            d = 0
            # cpu is high, default: 0
            # d = sum([psutil.Process(k).num_threads() for k in [x for x in psutil.pids()]])
        else:
            t,u,p,d = 0,0,0,0
        return t,u,p,d
    except:
        return 0,0,0,0



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
        avgrx = 0
        avgtx = 0
        for name, stats in psutil.net_io_counters(pernic=True).items():
            if "lo" in name or "tun" in name \
                    or "docker" in name or "veth" in name \
                    or "br-" in name or "vmbr" in name \
                    or "vnet" in name or "kube" in name:
                continue
            avgrx += stats.bytes_recv
            avgtx += stats.bytes_sent
        now_clock = time.time()
        netSpeed["diff"] = now_clock - netSpeed["clock"]
        netSpeed["clock"] = now_clock
        netSpeed["netrx"] = int((avgrx - netSpeed["avgrx"]) / netSpeed["diff"])
        netSpeed["nettx"] = int((avgtx - netSpeed["avgtx"]) / netSpeed["diff"])
        netSpeed["avgrx"] = avgrx
        netSpeed["avgtx"] = avgtx
        time.sleep(INTERVAL)

def _disk_io():
    """
    the code is by: https://github.com/giampaolo/psutil/blob/master/scripts/iotop.py
    good luck for opensource! modify: cpp.la
    Calculate IO usage by comparing IO statics before and
        after the interval.
        Return a tuple including all currently running processes
        sorted by IO activity and total disks I/O activity.
    磁盘IO：因为IOPS原因，SSD和HDD、包括RAID卡，ZFS等。IO对性能的影响还需要结合自身服务器情况来判断。
    比如我这里是机械硬盘，大量做随机小文件读写，那么很低的读写也就能造成硬盘长时间的等待。
    如果这里做连续性IO，那么普通机械硬盘写入到100Mb/s，那么也能造成硬盘长时间的等待。
    磁盘读写有误差：4k，8k ，https://stackoverflow.com/questions/34413926/psutil-vs-dd-monitoring-disk-i-o
    """
    while True:
        # first get a list of all processes and disk io counters
        procs = [p for p in psutil.process_iter()]
        for p in procs[:]:
            try:
                p._before = p.io_counters()
            except psutil.Error:
                procs.remove(p)
                continue
        disks_before = psutil.disk_io_counters()

        # sleep some time, only when INTERVAL==1 , io read/write per_sec.
        # when INTERVAL > 1, io read/write per_INTERVAL
        time.sleep(INTERVAL)

        # then retrieve the same info again
        for p in procs[:]:
            with p.oneshot():
                try:
                    p._after = p.io_counters()
                    p._cmdline = ' '.join(p.cmdline())
                    if not p._cmdline:
                        p._cmdline = p.name()
                    p._username = p.username()
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    procs.remove(p)
        disks_after = psutil.disk_io_counters()

        # finally calculate results by comparing data before and
        # after the interval
        for p in procs:
            p._read_per_sec = p._after.read_bytes - p._before.read_bytes
            p._write_per_sec = p._after.write_bytes - p._before.write_bytes
            p._total = p._read_per_sec + p._write_per_sec

        diskIO["read"] = disks_after.read_bytes - disks_before.read_bytes
        diskIO["write"] = disks_after.write_bytes - disks_before.write_bytes

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
            print("Connecting...")
            s = socket.create_connection((SERVER, PORT))
            data = s.recv(1024).decode()
            if data.find("Authentication required") > -1:
                s.send((USER + ':' + PASSWORD + '\n').encode("utf-8"))
                data = s.recv(1024).decode()
                if data.find("Authentication successful") < 0:
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
            if data.find("IPv4") > -1:
                check_ip = 6
            elif data.find("IPv6") > -1:
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
                MemoryTotal, MemoryUsed, SwapTotal, SwapUsed = get_memory()
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
                array['swap_used'] = SwapUsed
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

                s.send(("update " + json.dumps(array) + "\n").encode("utf-8"))
        except KeyboardInterrupt:
            raise
        except socket.error:
            print("Disconnected...")
            # keep on trying after a disconnect
            if 's' in locals().keys():
                del s
            time.sleep(3)
        except Exception as e:
            print("Caught Exception:", e)
            if 's' in locals().keys():
                del s
            time.sleep(3)
