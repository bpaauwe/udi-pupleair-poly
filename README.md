
# Purple Air 

This is a node server to pull AQI data from the Purple Air network and make it available to a [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)

(c) 2020 Robert Paauwe

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. Configure the node server per configuration section below.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to poll the Purple Air service for current AQI data (in seconds)
#### Long Poll
   * Not used
#### Custom Parameters
	* A list of Purple Air devices to monitor. For the 'key', enter a name to use to identify the device (under 14 characters, no special characters). For the 'value' enter the Purple Air sensor ID. This is typically just a number.

## Node substitution variables
### Controller node
 * sys.node.[address].ST      (Node sever online)

### Air Quality node
 * sys.node.[address].CLITEMP (current temperature)
 * sys.node.[address].CLIHUM  (current humidity)
 * sys.node.[address].BARPRES (current barometric pressure)
 * sys.node.[address].GV0     (current PM2.5 value speed)
 * sys.node.[address].GV1     (Age of data in days)
 * sys.node.[address].GV3     (10 minute average)
 * sys.node.[address].GV4     (30 minute average)
 * sys.node.[address].GV5     (60 minute average)
 * sys.node.[address].GV6     (6 hour average)
 * sys.node.[address].GV7     (24 hour average)
 * sys.node.[address].GV8     (1 week average)
 * sys.node.[address].GV10    (EPA Air Quality Index number)
 * sys.node.[address].GV11    (EPA Air Quality Index category)
 * sys.node.[address].GV12    (Data confidence)


## Requirements
1. Polyglot V2.
2. ISY firmware 5.0.x or later

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "Purple Air".

Then restart the Purple Air nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 1.0.4 08/31/2020
   - Fix confidence level calculation
- 1.0.3 08/31/2020
   - Remove test message
   - Trap and report connection errors
- 1.0.2 08/29/2020
   - Change to allow multiple Purple air device nodes.
- 1.0.1 08/29/2020
   - Add data confidence 
   - Fix typo
- 1.0.0 08/27/2020
   - Initial version.
