#ABOUT

This is a web application that displays list of candy manufacturers along with the names of candies manufactured by those particular manufacturers. It allows its users to signin using their google account and add, delete, edit the candies and manufacturers created by only them.

#FEATURES

Authorisation and authentication check using oAuth 2.0. Easy debugging due to flask implementation. Database implementation using SQLAlchemy.

### PROJECT STRUCTURE
```
.
├── application.py
├── client_secrets.json
├── database_setup.py
├── database_populator.py
├── candymanufacturers.db
├── README.md
├── static
│   └── style.css
└── templates
    ├── candies.html
    ├── deleteCandy.html
    ├── deleteManufacturer.html
    ├── editCandies.html
    ├── editManufacturer.html
    ├── header.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── newcandy.html
    ├── newManufacturer.html
    └── publiccandies.html
    ├── publicindex.html
    └── showcandydetails.html

```
### STEPS TO RUN THE PROJECT

* Unzip the downloaded folder named Finalfullstack
* Open a terminal window from the Finalfullstack/fullstack-nanodegree-vm/vagrant directory, or open a terminal window and cd into that directory.
* bring up the vagrant machine using
'''
vagrant up
'''
* login using secure shell by typing the following command
'''
vagrant ssh
'''
* cd into catalog folder
'''
cd catalog
'''
* First run the database_populator.py to insert some initial data into the database before running applicatio.py
'''
python database_populator.db
'''
* Now run the actual web application using the following command
'''
python application.py
'''
Open http://localhost:5059/ in a Web browser, enjoy.
