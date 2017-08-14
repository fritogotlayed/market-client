"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.

Based on knowledge gained by reading the source for winpcapy:
https://github.com/orweis/winpcapy
"""
# NOTE: We skip linting on this file since it is for interfacing with the C
# library pcap.
# pylint: disable-all
# pylint: skip-file
from ctypes import *
from ctypes.util import find_library
import sys

WIN32 = False

if sys.platform.startswith('win'):
    WIN32 = True

if WIN32:
    SOCKET = c_uint
    _lib = CDLL('wpcap.dll')
else:
    SOCKET = c_int
    _lib = CDLL(find_library('pcap'))


# # # # # Constants
PCAP_VERSION_MAJOR = 2
PCAP_VERSION_MINOR = 4
PCAP_ERRBUF_SIZE = 256
PCAP_IF_LOOPBACK = 1
MODE_CAPT = 0
MODE_STAT = 1


# # # # # Structures
class sockaddr(Structure):
    _fields_ = [('sa_family', c_ushort),
                ('sa_data', c_char * 14)]


class timeval(Structure):
    _fields_ = [('tv_sec', c_long),
                ('tv_usec', c_long)]


class pcap_pkthdr(Structure):
    _fields_ = [('ts', timeval),
                ('caplen', c_uint),
                ('len', c_uint)]


class pcap_addr(Structure):
    pass
pcap_addr._fields_ = [('next', POINTER(pcap_addr)),
                      ('addr', POINTER(sockaddr)),
                      ('netmask', POINTER(sockaddr)),
                      ('broadaddr', POINTER(sockaddr)),
                      ('dstaddr', POINTER(sockaddr))]


class pcap_if(Structure):
    pass
pcap_if._fields_ = [('next', POINTER(pcap_if)),
                    ('name', c_char_p),
                    ('description', c_char_p),
                    ('addresses', POINTER(pcap_addr)),
                    ('flags', c_uint)]

# # # # # Functions
pcap_handler = CFUNCTYPE(None,
                         POINTER(c_ubyte),
                         POINTER(pcap_pkthdr),
                         POINTER(c_ubyte))

# int   pcap_breakloop(c_void_p *)
#   Set a flag that will force pcap_dispatch() or pcap_loop() to return rather
#   than looping.
pcap_breakloop = _lib.pcap_breakloop
pcap_breakloop.restype = None
pcap_breakloop.argtypes = [POINTER(c_void_p)]

# void   pcap_close(c_void_p *p)
#   Close the files associated with p and deallocates resources.
pcap_close = _lib.pcap_close
pcap_close.restype = None
pcap_close.argtypes = [POINTER(c_void_p)]

# int   pcap_dispatch (c_void_p *p,
#                      int cnt,
#                      pcap_handler callback,
#                      u_char *user)
#   Collect a group of packets.
pcap_dispatch = _lib.pcap_dispatch
pcap_dispatch.restype = c_int
pcap_dispatch.argtypes = [POINTER(c_void_p),
                          c_int,
                          pcap_handler,
                          POINTER(c_ubyte)]

# int   pcap_findalldevs (pcap_if **alldevsp, char *errbug)
#   Construct a list of network devices that can be opened with pcap_open_live.
pcap_findalldevs = _lib.pcap_findalldevs
pcap_findalldevs.restype = c_int
pcap_findalldevs.argtypes = [POINTER(POINTER(pcap_if)), c_char_p]

# void   pcap_freealldevs(pcap_if *alldevsp)
#   Free an interface list returned by pcap_findalldevs.
pcap_freealldevs = _lib.pcap_freealldevs
pcap_freealldevs.restype = None
pcap_freealldevs.argtypes = [POINTER(pcap_if)]

# int   pcap_loop(c_void_p *p,
#                 int cnt,
#                 pcap_handler callback,
#                 u_char *user)
#   Collect a group of packets.
pcap_loop = _lib.pcap_loop
pcap_loop.restype = c_int
pcap_loop.argtypes = [POINTER(c_void_p), c_int, pcap_handler, POINTER(c_ubyte)]

# c_void_p *   pcap_open_live(const char *device,
#                             int snaplen,
#                             int promisc,
#                             int to_ms,
#                             char *ebuf)
#   Open a live capture from the network.
pcap_open_live = _lib.pcap_open_live
pcap_open_live.restype = POINTER(c_void_p)
pcap_open_live.argtypes = [c_char_p, c_int, c_int, c_int, c_char_p]
