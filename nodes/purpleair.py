#!/usr/bin/env python3
"""
Polyglot v2 node server Purple Air data
Copyright (C) 2020 Robert Paauwe
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import datetime
import requests
import socket
import math
import re
import json
import node_funcs
from datetime import timedelta

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'air quality'
    hint = [0,0,0,0]
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Puple Air AQI'
        self.address = 'pa'
        self.primary = self.address
        self.configured = False
        self.force = True
        self.host = 'https://www.purpleair.com/'
        self.uom = {
                'CLITEMP' : 17,
                'CLIHUM' : 22,
                'BARPRES' : 117,
                'GV0' : 56,
                'GV1' : 10,
                'GV2' : 56,
                'GV3' : 56,
                'GV4' : 56,
                'GV5' : 56,
                'GV6' : 56,
                'GV7' : 56,
                'GV8' : 56,
                'GV9' : 56,
                }

        self.params = node_funcs.NSParameters([{
            'name': 'Senosor ID',
            'default': 'set me',
            'isRequired': True,
            'notice': 'A Sensor ID must be set',
            },
            ])


        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        (valid, changed) = self.params.update_from_polyglot(config)
        if changed and not valid:
            LOGGER.debug('-- configuration not yet valid')
            self.removeNoticesAll()
            self.params.send_notices(self)
        elif changed and valid:
            LOGGER.debug('-- configuration is valid')
            self.removeNoticesAll()
            self.configured = True
            self.discover()
        elif valid:
            LOGGER.debug('-- configuration not changed, but is valid')

    def start(self):
        LOGGER.info('Starting node server')
        self.check_params()
        self.discover()
        LOGGER.info('Node server started')

        # Do an initial query to get filled in as soon as possible
        self.query_conditions()
        self.force = False

    def longPoll(self):
        LOGGER.debug('longpoll')
        #self.query_forecast()

    def shortPoll(self):
        self.query_conditions()

    def query_conditions(self):
        # Query for the current air quality conditions. We can do this fairly
        # frequently, probably as often as once a minute.

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return


        try:
            request = self.host + '?show=' + self.params.get('Sensor ID')

            c = requests.get(request)
            jdata = c.json()
            c.close()
            LOGGER.debug(jdata)

            if jdata == None:
                LOGGER.error('Current condition query returned no data')
                return

            results = jdata['results']

            if 'Label' in results[0]:
                LOGGER.info('Air Quality data for ' + results[0]['Label'])
            if 'Type' in results[0]:
                LOGGER.info('Air Quality sensor type ' + results[0]['Type'])

            if 'PM2_5Value' in results[0]:
                self.update_driver('GV0', results[0]['PM2_5Value'])

            if 'temp_f' in results[0]:
                self.update_driver('CLITEMP', results[0]['temp_f'])
            if 'humidity' in results[0]:
                self.update_driver('CLIHUM', results[0]['humidity'])
            if 'pressure' in results[0]:
                self.update_driver('BARPRES', results[0]['pressure'])

            if 'AGE' in results[0]:
                self.update_driver('GV1', results[0]['AGE'])

            if 'Stats' in results[0]:
                stats = resutls[0]['Stats']

                if 'v' in status:
                    self.update_driver('GV2', results[0]['v'])
                if 'v1' in status:
                    self.update_driver('GV3', results[0]['v1'])
                if 'v2' in status:
                    self.update_driver('GV4', results[0]['v2'])
                if 'v3' in status:
                    self.update_driver('GV5', results[0]['v3'])
                if 'v4' in status:
                    self.update_driver('GV6', results[0]['v4'])
                if 'v5' in status:
                    self.update_driver('GV7', results[0]['v5'])
                if 'v6' in status:
                    self.update_driver('GV8', results[0]['v6'])
                if 'p1' in status:
                    self.update_driver('GV9', results[0]['pm'])

        except Exception as e:
            LOGGER.error('Current observation update failure')
            LOGGER.error(e)


    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # Create any additional nodes here
        LOGGER.info("In Discovery...")

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):
        self.removeNoticesAll()

        if self.params.get_from_polyglot(self):
            LOGGER.debug('All required parameters are set!')
            self.configured = True
        else:
            LOGGER.debug('Configuration required.')
            LOGGER.debug('Sensor ID = ' + self.params.get('Sensor ID'))
            self.params.send_notices(self)

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                # level = self.getDriver('GVP')
                level = self.get_saved_log_level()
            except:
                LOGGER.error('set_logging_level: get saved log level failed.')

            if level is None:
                level = 30

            level = int(level)
        else:
            level = int(level['value'])

        # self.setDriver('GVP', level, True, True)
        self.save_log_level(level)
        LOGGER.info('set_logging_level: Setting log level to %d' % level)
        LOGGER.setLevel(level)

    commands = {
            'UPDATE_PROFILE': update_profile,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'DEBUG': set_logging_level,
            }

    # For this node server, all of the info is available in the single
    # controller node.
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'CLITEMP', 'value': 0, 'uom': 17},  # temperature
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'GV0', 'value': 0, 'uom': 56},      # current PM2.5
            {'driver': 'GV1', 'value': 0, 'uom': 10},      # age in days
            {'driver': 'GV2', 'value': 0, 'uom': 56},      # rt PM2.5
            {'driver': 'GV3', 'value': 0, 'uom': 56},      # 10 min avg
            {'driver': 'GV4', 'value': 0, 'uom': 56},      # 30 min avg
            {'driver': 'GV5', 'value': 0, 'uom': 56},      # 60 min avg
            {'driver': 'GV6', 'value': 0, 'uom': 56},      # 6 hr avg
            {'driver': 'GV7', 'value': 0, 'uom': 56},      # 24 hr avg
            {'driver': 'GV8', 'value': 0, 'uom': 56},      # 1 week avg
            {'driver': 'GV9', 'value': 0, 'uom': 56},      # rt PM2.5
            ]


