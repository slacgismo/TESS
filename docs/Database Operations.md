Requires database operations are implemented in the `database` module.  Note that most table are immutable. This means that changing the current value is actually a `INSERT` operation in the database.  

# Conformant table operations

In general there are four operations allowed on tables:

## `add`

The `add` operation is required to define a new entry in a table. Because all data is immutable and it must be possible to obtain the complete state of the system for any given time in the past, all `set` operations are implemented as `add` operations with table-specific semantics considered, e.g., `add` may require non-existence of a field value, and `set` may require existence of a field value.

## `get`

The `get` operation is required to get the data for an existing entry in a table. 

## `find`

The `find` operation is required to obtained the record id for an entry in a table.  By default, `find` operations obtain the most recently added entry that matches. If the date and time have been changed using the `set_clock` operation, `get` operations obtain the value that was in effect at the time.

## `set`

The `set` operation implements changes to existing entries in a table but submitting a new entry with a more recent `created` date/time.  A `set` operation does not change an existing record.


# Non-conformant table operations

A number of table operations do not necessarily satisfy the immutability requirement for table operations. All non-conforming table operations must be logged in the `log` date using a conforming table operation.

- `CREATE`: creation of new tables, fields, indexes, etc.

- `INSERT`: insertion of new records other than using an `add` operation

- `UPDATE`: update of existing records

- `DELETE`: delete of existing records

- `ALTER`: changes to tables, fields, indexes, etc.

- `LOAD`: bulk loading of data

- `DUMP`: bulk dumping of data


# Time control
~~~
set_clock(datetime=None)
~~~

Sets the time at which the database entries are to be returned.  Note that only `get` and `find` operations are affected by the clock. Setting the clock to `None` reset the clock to default behavior, i.e., obtain the most recent entry.

# Config

The `config` table stores data related to the general system configuration.

| Field name | Data type | Default value | Remarks
| ---------- | --------- | ------------- | --------------
| config_id  | integer   | autonum       | primary key
| system_id  | integer   | required      | constraint key
| name       | text      | required      |
| value      | text      | NULL          |
| created    | datetime  | autogen       | insert time

## `add_config`
~~~
add_config(name,value)
~~~

The `add_config` operation creates a new configuration variable. If the variable exists, the `add_config` operation fails with the error "{name} exists"

The initial variables defined for TESS operations are the following:

| Name          | Initial value              |
| ------------- | -------------------------- |
| api-version   | 1                          |
| mechanism     | AUCTION                    |
| interval      | 300                        |
| time-unit     | h                          |
| currency-unit | $                          |
| admin-email   | dchassin@slac.stanford.edu |

## `get_config`
~~~
get_config(config_id)
~~~

The `get_config` operation gets the value for the specified `config_id`.  

## `find_config`
~~~
find_config(name)
~~~

The `find_config` operation obtains the current value of the config variable `name`. If the `set_clock` operation has been used, the value obtained will be for the datetime specified.

## `set_config`
~~~
set_config(name,value)
~~~

The `set_config` operation sets the current value of a configuration variable. If the config entry `name` does not exist the operation fails with the error "{name} not found"


# Device

The `device` table stores data related to devices that participate in the TESS market operations. 

| Field name | Data type | Default value | Remarks
| ---------- | --------- | ------------- | --------------
| device_id  | integer   | autonum       | primary key
| user_id    | integer   | required      | constraint key
| name       | text      | required      |
| unique_id  | text      | autogen       | unique key
| created    | datetime  | autogen       | insert time

## `add_device`

## `get_device`

## `find_device`

## `set_device`


# Log

The `log` table stores data related to non-conforming database operations during TESS market operations. Log entries are required for all events that are not otherwise recorded in other tables.  The following events must be logged:

- Database creation
- Database backup
- Database restore
- Database operations that do not strictly conform to the database immutability requirement (e.g., `INSERT`, `UPDATE`, `DELETE`, `ALTER`).

## `add_log`

## `get_log`


# Meter

The `meter` table stores data related to meters that record device behavior for the purpose of generating transactions.

## `add_meter`

## `get_meter`

## `find_meter`

## `set_meter`


# Order

The `order` table stores data related to buy and sell orders placed by devices.

## `add_order`

## `get_order`

## `find_order`

## `set_order`


# Preference

The `preference` table stores data related to user preferences for mobile and web applications they user.

## `add_preference`

## `get_preference`

## `find_preference`

## `set_preference`


# Price

The `price` table stores data related to prices generated by market operations.

## `add_price`

## `get_price`

## `find_price`

## `set_price`


# Resource

The `resource` table stores data related to resources that are available through the TESS market operations.

## `add_resource`

## `get_resource`

## `find_resource`

## `set_resource`


# Setting

The `setting` table stores data related to settings for devices that users own.

## `add_setting`

## `get_setting`

## `find_setting`

## `set_setting`

# System

The `system` table stores data related to systems that participate in the TESS market operations.

## `add_system`

## `get_system`

## `find_system`

## `set_system`


# Token

The `token` table stores data related to access tokens generated by users and devices.

## `add_token`

## `get_token`

## `find_token`

## `set_token`


# Transaction

The `transaction` table stores data related to transactions arising from device metering.

## `add_transaction`

## `get_transaction`

## `find_transaction`

## `set_transaction`


# User

The `user` table stores data related to user that participate in the TESS market operations.

## `add_user`

## `get_user`

## `find_user`

## `set_user`

