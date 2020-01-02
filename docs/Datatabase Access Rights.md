There are two types of connections `ALL`owed to the TESS database in MySQL, `admin` and `user`. Admin users have all access rights. Regular users have `SELECT` access to all tables, and `INSERT` rights to tables involving user data.

Table 1: Database Access Rights

| Table         | Admin | User              |
| ------------- | ----- | ----------------- |
| `config`      | `ALL` | `SELECT`          |
| `device`      | `ALL` | `SELECT`,`INSERT` |
| `log`         | `ALL` | `SELECT`          |
| `meter`       | `ALL` | `SELECT`,`INSERT` |
| `order`       | `ALL` | `SELECT`,`INSERT` |
| `preference`  | `ALL` | `SELECT`,`INSERT` |
| `price`       | `ALL` | `SELECT`          |
| `resource`    | `ALL` | `SELECT`          |
| `setting`     | `ALL` | `SELECT`          |
| `system`      | `ALL` | `SELECT`          |
| `token`       | `ALL` | `SELECT`,`INSERT` |
| `transaction` | `ALL` | `SELECT`          |
| `user`        | `ALL` | `SELECT`          |

