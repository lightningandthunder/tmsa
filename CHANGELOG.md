### 0.6.0
- Rewrote most chart code
- Enabled PVP aspects
- Fixed natal ecliptical aspects from showing up in return charts
- Background options: rename "Eureka curve" to "Cadent" and "Cadent" to "TMSA Classic"
- Switched from default options files to in-code data structures
- Migrated "Default_XYZ" option files to "XYZ_Default"
- Changed mundane midpoint calculation to use the closest angular contact among angle axes that both planets are foreground on
- Included version number and option to recalculate the radix when version number is too low for solunars to be correctly calculated
- New midpoint calculations are now written to the Cosmic State report
- Added angles (Ascendant, Midheaven, Eastpoint, and Vertex) to the data table
- Added calculation for planetary stations
- Removed same-planet aspects in solunar returns
- Added needs hierarchy scores for natal charts
- Shortened column headers
- Ecliptical/mundane aspects are compared by strength %, not raw orb
- Added button text auto-resizing
- Enabled experimental planets (Eris, Haumea, asteroids, other TNOs)
- Fixed declination calculations for vertex and ascendant

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