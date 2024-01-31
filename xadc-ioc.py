#!/usr/bin/env python3

import re
import sys
import yaml
import socket
import requests
import threading

from pcaspy import SimpleServer, Driver
from epics import PV

requests.packages.urllib3.disable_warnings()

iiodev = "/sys/bus/iio/devices/iio:device0/"

# IOC scan period (in seconds)
freq = 1

pvdb = {
   'TEMP' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_temp0_raw'),
      'scale': 123.040771484 / 1000,
      'offset': -2219,
      'unit': 'C',
    },
   'VCCINT' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage0_vccint_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VCCAUX' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage1_vccaux_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VCCBRAM' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage2_vccbram_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VCCPINT' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage3_vccpint_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VCCPAUX' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage4_vccpaux_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VCCODDR' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage5_vccoddr_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VREFP' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage6_vrefp_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
   'VREFN' : {
      'prec' : 3,
      'mdel': -1,
      'scan' : freq,
      'fd': open(f'{iiodev}/in_voltage7_vrefn_raw'),
      'scale': 0.732421875 / 1000,
      'offset': 0,
      'unit': 'V',
    },
}

class myDriver(Driver):
   def __init__(self):
      super(myDriver, self).__init__()

   def read(self, reason):
      if reason in pvdb:
         raw = (int)(pvdb[reason]['fd'].read())
         value = (raw + pvdb[reason]['offset']) * pvdb[reason]['scale']
         pvdb[reason]['fd'].seek(0)
      else:
         value = self.getParam(reason)
   
      return value

   def write(self, reason, value):
      # disable PV write (caput)
      return True
class HttpThread(threading.Thread):
   def __init__(self, kwargs=None):
      threading.Thread.__init__(self, args=(), kwargs=None)
         
      self.name = "HttpThread"
      self.hostname = kwargs['hostname']
      self.url = kwargs['url']
      self.username = kwargs.get('username', None)
      self.password = kwargs.get('password', None)
      self.pvprefix = kwargs['pvprefix']
      self.payloads = []
      self.pvs = []
      self.mutex = threading.Lock()
      self.daemon = True
   
   def run(self):
      print(f'{threading.current_thread().name}')

      # wait for PV valid values
      time.sleep(2)

      while True:
   
         # relax CPU
         time.sleep(2)

      print(f'{threading.current_thread().name} exit')

if __name__ == '__main__':

   # get hostname
   hostname = socket.gethostname().split(".")[0] 

   # default PVs prefix
   prefix = "PS:"

   threads = []

   config = {}
   try:
      with open(f"{sys.path[0]}/config.yaml", "r") as stream:
         try:
            config = yaml.safe_load(stream)
         except yaml.YAMLError as e:
            print(e) 
            exit(-1)
         else:
            for section in config:

               if 'epics' in section:
                  # resolve macro
                  prefix = section['epics'].get('prefix', 'ZYNQ:')
                  prefix = re.sub('\$hostname', hostname, prefix.lower()).upper()

               if 'http' in section:
                  if section['http'].get('enable', False):
                     args = {}
                     args['hostname'] = hostname
                     args['url'] = section['http'].get('url', None)
                     if args['url'] is None:
                        print("ERROR: HTTP section enabled but 'url' parameter is not provided")
                        exit(-1)
                     args['username'] = section['http'].get('username', None)
                     args['password'] = section['http'].get('password', None)
                     args['pvprefix'] = prefix
                     threads.append(HttpThread(kwargs=args))

   except (FileNotFoundError, PermissionError) as e:
      print(f'WARNING: {e} - running with defaults')
      pass

   server = SimpleServer()
   server.createPV(prefix, pvdb)
   driver = myDriver()

   # process CA transactions
   while True:
      server.process(0.1)
