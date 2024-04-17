# Fixtures

This folder contains fixtures: data used to seed the initial state of the database during testing and deployment.

## File Structure

- TOML format.
- Each file contains only rows for a single table.
- Each file specifies a unique identifier (`fixture_id`) for that fixture. This ID is not pushed to the database. We often use UUID
  values for these but this is not required; they only need to be unique.
- Each file optionally specifies a `requires_id`. This ID is used to determine what order each fixture should be loaded in.

### Examples

####  company.toml
```
table_name = "company"
fixture_id = "4ca29ff8-eb75-4166-8f8f-26e2d9ba1f42"

[[row]]
id = "dbd4581f-767f-42df-b48f-cd343a0a83c1"
created_on = 1658598374097997
name = "DataKitchen"
```

#### organization.toml
```
table_name = "organization"
fixture_id = "d2eb73bb-0329-4607-b659-5ec9905f9428"
requires_id = "4ca29ff8-eb75-4166-8f8f-26e2d9ba1f42"

[[row]]
id = "0d21dfd0-6490-4d1e-8365-36fd7a1ba99d"
created_on = 1658598374097997
name = "default"
description = ""
company = "dbd4581f-767f-42df-b48f-cd343a0a83c1"
```

## CLI Tools


### ``load``

There is a ``load-fixture`` subcommand for ``cli``. It can be given either a specific file to load OR a folder with
multiple fixtures to load.

Example:

```bash
$ cli load-fixture /path/to/fixtures/development
```

### ``dump``

There is a ``dump-fixture`` subcommand for ``cli``. It takes a table argument (the name of the model schema class)
and will dump a fixture file of all the rows for that table. This can be useful for setting up data from small local
environments and using that data to make fixtures. It can output to standard out or to a file.


Example:

```bash
$ cli dump-fixture Company --output company-fixture.toml
```
