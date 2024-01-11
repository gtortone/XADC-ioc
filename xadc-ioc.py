#!/usr/bin/env python3

import argparse
from pcaspy import SimpleServer, Driver

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

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('-p', '--prefix', action='store', help='EPICS PV prefix (default: \'ZYNQ:\')', default="ZYNQ:")
   args = parser.parse_args()

   server = SimpleServer()
   server.createPV(args.prefix, pvdb)
   driver = myDriver()

   # process CA transactions
   while True:
      server.process(0.1)
