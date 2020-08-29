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
from nodes import sensor
from datetime import timedelta

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'controller'
    hint = [0,0,0,0]
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Purple Air AQI'
        self.address = 'pa'
        self.primary = self.address
        self.configured = False
        self.force = True
        self.sensor_list = {}
        self.in_config = False
        self.in_discover = False

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        rediscover = False
        if self.in_config:
            return

        self.in_config = True
        if 'customParams' in self.polyConfig:
            for sensor_name in self.polyConfig['customParams']:
                LOGGER.info('Found Purple Air sensor ID ' + sensor_name + ' with ID ' + self.polyConfig['customParams'][sensor_name])
                if sensor_name not in self.sensor_list:
                    sensor_id = self.polyConfig['customParams'][sensor_name]
                    self.sensor_list[sensor_name] = {'id': sensor_id, 'configured': False}
                    rediscover = True

        if rediscover:
            self.discover()
            self.shortPoll()

        self.in_config = False

    def start(self):
        LOGGER.info('Starting node server')
        self.set_logging_level()
        self.check_params()
        self.discover()
        LOGGER.info('Node server started')
        self.force = False

        self.shortPoll()

    def longPoll(self):
        LOGGER.debug('longpoll')

    def shortPoll(self):
        for node in self.nodes:
            if self.nodes[node].address != self.address:
                LOGGER.error('Testing: calling short poll for ' + node)
                self.nodes[node].shortPoll()

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # Create nodes for each sensor here
        if self.in_discover:
            return

        self.in_discover = True
        LOGGER.info("In Discovery...")
        for sensor_name in self.sensor_list:
            LOGGER.debug(self.sensor_list[sensor_name])
            if self.sensor_list[sensor_name]['configured']:
                LOGGER.info('Sensor ' + sensor_name + ' already configured, skipping.')
                continue

            try:
                node = sensor.SensorNode(self, self.address, self.sensor_list[sensor_name]['id'], sensor_name)
                node.configure(self.sensor_list[sensor_name]['id'])
                LOGGER.info('Adding new node for ' + sensor_name)
                self.addNode(node)
                self.sensor_list[sensor_name]['configured'] = True
            except Exception as e:
                LOGGER.error(str(e))

        self.in_discover = False


    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):
        if 'customParams' in self.polyConfig:
            for sensor_name in self.polyConfig['customParams']:
                LOGGER.info('Found Purple Air sensor ID ' + sensor_name + ' with ID ' + self.polyConfig['customParams'][sensor_name])
                if sensor_name not in self.sensor_list:
                    sensor_id = self.polyConfig['customParams'][sensor_name]
                    self.sensor_list[sensor_name] = {'id': sensor_id, 'configured': False}
        else:
            LOGGER.error('Config not found')

        self.removeNoticesAll()

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


