# Meter API

[add description here...]

## API Endpoints

| Operation  | Endpoint             | Description                 |
-------------|----------------------------------------------------|
|GET         |/api/v1/meters        |List or search meters        |
|GET         |/api/v1/meters/123    |Get meter #123               |
|PUT         |/api/v1/meters/123    |Modify meter #123            |
|POST        |/api/v1/meters/123    |Add meter #123               |
|GET         |/api/v1/meter/meta    |Get meter schema             |


## Attributes
| Attribute        | Format                  | Description                                         | Example                           |
-------------------|-------------------------------------------------------------------------------|-----------------------------------
|uid               |UID String               |Unique id for meter                                  |"xyz123p" |
|utility_uid       |UID String               |Unique id for utility to which the meter belongs     |"xyz123p" |
|authorization_uid |UID String               |The authorization under which meter belongs          |"xyz123p" |
|user_uid          |UID String               |Unique id for meter owner                            |"xyz123p" |
|meter_type?       |???????                  |                                                     |"" |
|status            |String                   |      | |
|is_archived       |Boolean                  |Whether meter data is Archived or Active             |"True" or "False" |
|is_active         |Boolean                  |Whether meter data is Archived or Active             |"True" or "False" |
|created           |ISO8601 Timestamp        |When the meter was created                           |"2020-03-20T11:21:33.123456+00:00" |
|service_location  |Integer?                 |                                                     |"" |
|postal_code       |String                   |                                                     |"" |
|map_location      |Integer?                 |                                                     |"" |
|channel?          |Integer                  |  |"" |
|feeder            |Integer?                 |                                                     |"" |
|substation        |Integer?                 |                                                     |"" |
|rate              |String                   |                                                     |"" |
|interval_count    |Integer                  |Number of intervals collected                        |"123456" |
|interval_coverage |List of ISO8601 tuples   |Timespans covered by intervals collected             |"" |
|unit              |String                   |                                                     |"" |
|exports           |List of name, URL tuples |List of name and URLs to various meter data downloads|"" |


## JSON Object Example
