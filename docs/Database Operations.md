Requires database operations are implemented in the `database` module.  Note that most table are immutable. This means that changing the current value is actually a `INSERT` operation in the database.  

# Time control
~~~
set_clock(datetime=None)
~~~

Sets the time at which the database values are to be completed.  Note that only `get` operations are affected by the clock. Setting the clock to `None` returns to real-time operations.

# Config

The `config` table stores data related to the general system configuration.

| Field name | Data type | Default value | Remarks
| ---------- | --------- | ------------- | ------------
| config_id  | integer   | auto          | primary key
| system_id  | integer   | required      | constrained key
| name       | text      | required      |
| value      | text      | NULL          |
| created    | datetime  | current time  |

## `create_config`
~~~
create_config(name,initial_value)
~~~

The `create_config` operation creates a new configuration variable.

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
get_config(name)
~~~

The `get_config` operation gets the current value of a configuration variable.  If the `set_clock` operation has been used, the value obtained will be for the datetime specified.

## `change_config`
~~~
change_config(name,new_value)
~~~

The `change_config` operation sets the current value of a configuration variable.

# Device

TODO

# Log

TODO

# Meter

TODO

# Preference

TODO

# Price

TODO

# Resource

TODO

# Setting

TODO

# System

TODO

# Token

TODO

# Transaction

TODO

# User

TODO
