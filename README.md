# Item-catalog

> A very minimal catalog application displaying a book shelf.

## Features
* Displays genres(categories) and books(items)
* Provides a third-party authentication system
    * Google
    * Facebook
* Implements API endpoints with JSON response format
* Leverages Flask Python framework for the backend and Bootstrap CSS framework for the frontend

## Setup
* Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository which contains the required dependencies.
```
$ git clone https://github.com/udacity/fullstack-nanodegree-vm.git
```

* Move into the `fullstack-nanodegree-vm/vagrant` folder and clone the current repository.
```
$ cd fullstack-nanodegree-vm/vagrant
$ git clone https://github.com/nirajpandkar/item-catalog.git 
```

* Launch the vagrant VM from inside the `vagrant` folder.
```
$ vagrant up
$ vagrant ssh
```

* Install dependencies
    * You could install dependencies individually
    ```
    $ sudo apt-get install update
    $ sudo apt-get install python-flask python-sqlalchemy
    $ sudo apt-get install python-pip
    $ sudo pip install requests
    $ sudo pip install httplib2
    $ sudo pip install oauth2client
    ```
    OR use this shell script which achieves the same.
    ```
    ./item_catalog.sh
    ```
    
* Move inside the `item-catalog` folder and setup the required database.
```
$ cd item-catalog
```

* Create user 'catalog' and database 'catalog' in postgresql.
```
$ sudo -u postgres psql postgres
postgres=# create user catalog with password 'superman1$';
postgres=# create database catalog owner catalog;
postgres=# \q
```

* Populate the database
```
$ python populate_database.py
```

* Run the application locally.
```
$ python ItemCatalog.py
```


* You'll be able to browse the application at this url(Auth is configured for 'localhost')- 

    `http://localhost:5000/`
    
## JSON API endpoints

| Endpoints       | Description           |
| ------------- |:-------------:|
| /categories/JSON      | Get information about all the genres |
| /users/JSON      | Get information about all the users      |
| /category/{genre}/items/JSON      | Get information about all the books in a particular genre     |
| /category/{genre}/{book}/JSON | Get information about a particular book in a particular genre      |

## Future Scope
* Add author, rating, published year
* Add user's picture to enhance profile
## License

MIT © [Niraj Pandkar](https://github.com/nirajpandkar)