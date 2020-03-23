# Meter API

[add description here...]

## API Endpoints

| Operation  | Endpoint             | Description                 |
-------------|----------------------------------------------------|
|GET         |/api/v1/meters        |List or search meters        |
|GET         |/api/v1/meters/123    |Get meter #123               |
|PUT         |/api/v1/meters/123    |Modify meter #123            |


## Attributes
| Attribute        | Format                  | Description                                         | Example                           |
-------------------|-------------------------------------------------------------------------------|-----------------------------------
|uid               |UID String               |Unique id for meter                                  |"xyz123p" |
|utility_uid       |UID String               |Unique id for utility to which the meter belongs     |"xyz123p" |
|authorization_uid |UID String               |The authorization under which meter belongs          |"xyz123p" |
|user_uid          |UID String               |Unique id for meter owner                            |"xyz123p" |
|meter_type?       |???????                  |                                                     |"" |
|status            |String                   |      | |
|telemetry_ status |String                   |Whether meter data is Archived or Active             |"Archived" or "Active" |
|created           |ISO8601 Timestamp        |When the meter was created                           |"2020-03-20T11:21:33.123456+00:00" |
|service_location  |Integer                  |                                                     |"" |
|zipcode           |Integer                  |                                                     |"" |
|map_location      |Integer                  |                                                     |"" |
|channel?          |Integer                  |Is this only relevant for virtual metering or meter collection? |"" |
|feeder            |Integer                  |                                                     |"" |
|substation        |Integer                  |                                                     |"" |
|rate              |String                   |                                                     |"" |
|interval_count    |Integer                  |Number of intervals collected                        |"123456" |
|interval_coverage |List of ISO8601 tuples   |Timespans covered by intervals collected             |"" |
|unit              |String                   |                                                     |"" |
|exports           |List of name, URL tuples |List of name and URLs to various meter data downloads|"" |
