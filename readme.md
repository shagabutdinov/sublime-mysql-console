Sublime MysqlConsole
====================

Run mysql/postgresql query from command line.


### Features

Allows to setup connection from sublime to mysql or postgresql server, send
queries and receive their results.


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### Usage

* Set your project settings like in the example:

```
# psql

{
  "folders": [<...>],
  "settings": {
    "pgsql": [
      "psql",
      "--host",
      "localhost",
      "--port",
      "5432",
      "--username",
      "user",
      "--no-password",
      "database",
    ],
    "pgsql_password": "password",
  }
}

# mysql

{
  "folders": [<...>],
  "settings": {
    "mysql": [
      "mysql",
      "--host",
      "localhost",
      "--port",
      "3306",
      "--user",
      "user",
      "--password",
      "password",
    ],
  }
}
```

* Open sql console with `ctrl+u, ctrl+q`

* Type example query:

```
# psql

\x;

# mysql
SHOW TABLES;
```

* Set cursor position right after ";" and hit enter in order to see the result


### Commands

| Description        | Keyboard shortcuts | Command palette            |
|--------------------|--------------------|----------------------------|
| Open Mysql Console | ctrl+u, ctrl+q     | MysqlConsole: Open Console |
| Run Mysql Query    | enter              | MysqlConsole: Run Query    |


### Dependencies

* [expression](https://github.com/shagabutdinov/sublime-expression)
