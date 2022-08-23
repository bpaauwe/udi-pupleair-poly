#!/usr/bin/env python3
"""
Polyglot v2 node server Purple Air data
Copyright (C) 2020 Robert Paauwe
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import requests
import json
import node_funcs

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class SensorNode(polyinterface.Node):
    # class variables
    id = 'aqi'
    hint = [0,0,0,0]
    status= None

    def __init__(self, controller, primary, address, name):
        # call the default init
        super(SensorNode, self).__init__(controller, primary, address, name)

        self.host = ''
        self.headers = ''
        self.configured = False;
        self.uom = {
                'CLITEMP' : 17,
                'CLIHUM' : 22,
                'BARPRES' : 117,
                'GV0' : 56,
                'GV1' : 45,
                'GV2' : 56,
                'GV3' : 56,
                'GV4' : 56,
                'GV5' : 56,
                'GV6' : 56,
                'GV7' : 56,
                'GV8' : 56,
                'GV9' : 56,
                'GV10' : 56,
                'GV11' : 25,
                'GV12' : 51,
                }


    drivers = [
            {'driver': 'CLITEMP', 'value': 0, 'uom': 17},  # temperature
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'GV0', 'value': 0, 'uom': 56},      # current PM2.5
            {'driver': 'GV1', 'value': 0, 'uom': 45},      # age in minutes
            {'driver': 'GV3', 'value': 0, 'uom': 56},      # 10 min avg
            {'driver': 'GV4', 'value': 0, 'uom': 56},      # 30 min avg
            {'driver': 'GV5', 'value': 0, 'uom': 56},      # 60 min avg
            {'driver': 'GV6', 'value': 0, 'uom': 56},      # 6 hr avg
            {'driver': 'GV7', 'value': 0, 'uom': 56},      # 24 hr avg
            {'driver': 'GV8', 'value': 0, 'uom': 56},      # 1 week avg
            {'driver': 'GV10', 'value': 0, 'uom': 56},     # AQI
            {'driver': 'GV11', 'value': 0, 'uom': 25},     # AQI string
            {'driver': 'GV12', 'value': 0, 'uom': 51},     # confidence
            ]


    def configure(self, sensor, apikey):
        self.host = 'https://api.purpleair.com/v1/sensors/' + sensor
        self.headers = {'X-API-Key':apikey}
        self.configured = True

    def epa_aqi(self, pm25):
        aqi = 0
        breakpoints = [
                [0, 12],
                [12.1, 35.4],
                [35.5, 55.4],
                [55.5, 150.4],
                [150.5, 250.4],
                [250.5, 500.4],
                ]
        indexes = [
                [0, 50],
                [51, 100],
                [101, 150],
                [151, 200],
                [201, 300],
                [301, 500],
                ]

        pm25 = round(pm25,1)

        # find the breakpoints for the pm25 value
        try:
            for bpi in range(0,6):
                if pm25 >= breakpoints[bpi][0] and pm25 <= breakpoints[bpi][1]:
                    break
        except Exception as e:
            LOGGER.error('AQI_bp: ' + str(e))
        
        if bpi == 6:
            LOGGER.error('AQI out of range!')
            return

        try:
            aqi = ((indexes[bpi][1] - indexes[bpi][0]) / (breakpoints[bpi][1] - breakpoints[bpi][0])) * (pm25 - breakpoints[bpi][0]) + indexes[bpi][0]
        except Exception as e:
            LOGGER.error('AQI_calc: ' + str(e))

        LOGGER.debug('Calculated AQI = ' + str(aqi))
        return (round(aqi, 0), indexes[bpi][0])

    def calculate_confidence(self, results):
        channel_a = results[0]
        channel_b = results[1]

        if 'AGE' in channel_a and 'AGE' in channel_b:
            if channel_a['AGE'] != channel_b['AGE']:
                LOGGER.error('data channels age differs, bad data!')
                return 0
        else:
            LOGGER.error('missing data age info.')
            return 0

        if 'PM2_5Value' in channel_a and 'PM2_5Value' in channel_b:
            A = float(channel_a['PM2_5Value'])
            B = float(channel_b['PM2_5Value'])

            C = 100 - abs(((A - B) / (A + B)) * 100)
            return round(C, 0)
        else:
            LOGGER.error('missing data for PM2.5.')
            return 0


    def shortPoll(self):
        # Query for the current air quality conditions. We can do this fairly
        # frequently, probably as often as once a minute.

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return


        try:
            c = requests.get(self.host, headers=self.headers)
            try:
                jdata = c.json()
            except:
                LOGGER.error('Connection issue: ' + str(c))
                c.close()
                return

            c.close()
            LOGGER.debug(jdata)

            if jdata == None:
                LOGGER.error('Current condition query returned no data')
                return

            sensor = jdata['sensor']

            if 'name' in sensor:
                LOGGER.info('Air Quality data for ' + sensor['name'])
            if 'model' in sensor:
                LOGGER.info('Air Quality sensor type ' + sensor['model'])

            if 'pm2.5' in sensor:
                self.update_driver('GV0', sensor['pm2.5'])
                (aqi, idx) = self.epa_aqi(float(sensor['pm2.5']))
                self.update_driver('GV10', aqi)
                self.update_driver('GV11', idx)

            if 'confidence' in sensor:
                LOGGER.info('Data confidence level = ' + str(sensor['confidence']) + '%')
                self.update_driver('GV12', sensor['confidence'])
            if 'temperature' in sensor:
                self.update_driver('CLITEMP', sensor['temperature'])
            if 'humidity' in sensor:
                self.update_driver('CLIHUM', sensor['humidity'])
            if 'pressure' in sensor:
                self.update_driver('BARPRES', sensor['pressure'])

            # age is difference between jdata[time_stamp] and sensor['last_seen']
            #  in minutes
            if 'time_stamp' in jdata and 'last_seen' in sensor:
                age = (jdata['time_stamp'] - sensor['last_seen']) / 60
                self.update_driver('GV1', age)

            if 'stats' in sensor:
                stats = sensor['stats']
                if 'pm2.5_10minute' in stats:
                    self.update_driver('GV3', stats['pm2.5_10minute'])
                if 'pm2.5_30minute' in stats:
                    self.update_driver('GV4', stats['pm2.5_30minute'])
                if 'pm2.5_60minute' in stats:
                    self.update_driver('GV5', stats['pm2.5_60minute'])
                if 'pm2.5_6hour' in stats:
                    self.update_driver('GV6', stats['pm2.5_6hour'])
                if 'pm2.5_24hour' in stats:
                    self.update_driver('GV7', stats['pm2.5_24hour'])
                if 'pm2.5_1week' in stats:
                    self.update_driver('GV8', stats['pm2.5_1week'])

        except Exception as e:
            LOGGER.error('Current observation update failure')
            LOGGER.error(e)

