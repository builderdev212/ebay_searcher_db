# Overview

A small project I made to easily search through ebay listings.
Based on [this blog post](https://dev.to/dmitryzub/scrape-ebay-search-with-python-2h22).
sqlite3 multithreaded from [this post](https://stackoverflow.com/questions/41206800/how-should-i-handle-multiple-threads-accessing-a-sqlite-database-in-python).

The search you make is saved as a sqlite3 database.
There is no built in data browser, as I used [DB Browser for SQLite](https://sqlitebrowser.org/).

# Required Software
*This does not mean that this code cannot run on other versions of this software.*
*These are just the library versions I ran them on.*

**PYTHON VERSION:** 3.10.5

**REQUIRED LIBRARIES**
- lxml (*version 4.9.1*)
- beautifulsoup4 (*version 4.11.1*)
