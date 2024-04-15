# Overview

This document attempts to identify how data will be populated and move through
the alert authoring system.

## DataFlows

### Create Alert

A net new alert is created.  The following actions take place:

* New alert record is created
* One or more alert junction records are created.  These records maintain the
  relationship between an alert and alert levels and areas to which they apply

#### CAP Events created

CAP events are amalgamations of alerts areas for a given alert, that have the
the same alert levels.

##### Scenario 1

Two area are effected with the same alert levels:
* basin 1 - High Streamflow advisory
* basin 2 - High Streamflow advisory

Cap Events Emitted:
* Event 1 - basin 1 and basin 2 - High Streamflow advisory


##### Scenario 2

Two areas are effected with different alert levels:
* basin 1 - High Streamflow Advisory
* basin 2 - Flood Watch

Cap Events Emitted:
* Event 1 - basin 1 High Streamflow Advisory
* Event 2 - basin 2 - Flood watch

