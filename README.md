# Item-catalog

> A very minimal catalog application.

## Setup
* Clone the project and cd into it.
`git clone https://github.com/nirajpandkar/item-catalog.git`
`cd item-catalog`

* Create a virtual environment and activate it.
`virtualenv venv`
`source venv/bin/activate`
**Note**: May need to use `sudo` when inside priveleged folders like `/var/www/html`

* Install following dependencies.
`pip install flask`
`pip install sqlalchemy`

* Create the database.
`python database.py`

* Populate the database.
`python populate_data.py`

* Run the main script.
`python ItemCatalog.py`

**Note**: May need to use `sudo` rights when necessary.