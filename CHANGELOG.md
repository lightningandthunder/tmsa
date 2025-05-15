### 0.7.0
- Added paran functionality
- Enabled minor aspects, including 10° series
- Added pagination to "recently used" items, increasing the storage size
- Removed the legacy "TMSA Classic" angularity model
- Aspects now split into columns even if there are missing classes
- Added many Solunar return types: Novienic Solar Returns (Enneads), Novienic Lunar Returns, Anlunars, Solilunars, and Lunisolars.
- Made "angle contact aspects" have the same strength scale as traditional aspects
- Added a "Sidereal Landmarks" page
- Refreshed the Solunars page to allow for all of the additional Solunar types
- Added a toggle under Program Options to disable quarti-returns, removing them from all menus
- Fixed "All Solunars for 1 Year" toggle to correctly fetch all selected Solunars
- Fixed MC altitude calculation for southern latitudes
- Under the hood: changed the way chart data calculation happens and gets saved to streamline multi-step charts such as Anlunar Returns.
- Fixed bug where midpoint halfsums would get calculated more than once, wasting time

### 0.6.0

#### Data Table
- Added angles (Ascendant, Midheaven, Eastpoint, and Vertex) to the data table

#### Aspect Calculation
- Enabled PVP aspects
- Suppressed natal ecliptical aspects from showing up in return charts
- Changed mundane midpoint calculation to use the closest angular contact among angle axes that both planets are foreground on
- Required midpoint contacts to minor angles to have both planets in the halfsum be foreground on that angle
- Added angle contacts above the aspectarian
- Midpoints can now be calculated for polywheels
- Removed same-planet aspects in solunar returns
- Ecliptical/mundane aspects are now compared by strength %, not raw orb
- Enabled Inconjunct aspect types (semisextile and quincunx)

#### Cosmic State Report
- Added calculations for planetary stations, which now appear in Cosmic State
- Added a Needs Hierarchy score for natal charts to Cosmic State


#### Look and Feel
- Background options: renamed "Eureka curve" to "Cadent" and "Cadent" to "TMSA Classic"
- Shortened column headers
- Added button text auto-resizing
- Added Show Errors button on the main page to open the error log file
 
#### Other
- Rewrote most chart code
- Enabled experimental planets (Eris, Haumea, asteroids, other TNOs)
- Switched from default options files to in-code data structures
- Migrated "Default_XYZ" option files to "XYZ_Default"
- Included version number and option to recalculate the radix when version number is too low for solunars to be correctly calculated
- Turned off "other partile aspects" by default for ingresses
- Turned on PVP aspects by default for ingresses
- And probably more!

### 0.5.7
- Fixed bug where mundane midpoints were using meridian longitude instead of prime vertical longitude
- Better error message when clicking predictive options

### O.5.6
- Fixed background planets showing as foreground in cosmic state
s
### 0.5.5
- Fixed bug where planets mundanely background wouldn't be considered for aspects even if they were on a minor angle

### 0.5.0
- Changed strength calculation for minor angles
- Added calculations for meridian longitude
- Added Blue for code formatting
- Added calculations for Vertex/Antivertex contacts in azimuth
- Stopped autotabbing while typing in form fields
- Included support for Linux
- Refactored uniwheels
- Added vertical scaling to title screen
- Added text wrap to buttons
- Enabled single-formula "Eureka" angularity curve

### 0.4.13
- Moved to semantic versioning (major.minor.patch format)
- Added AGPL licenses as required by the Swiss Ephemeris
- Added copyright information
- Added dependencies to etc\requirements.txt
- Fixed button labels so they don't get cut off
- Improved startup speed (...somehow)