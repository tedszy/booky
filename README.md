# booky the Bookbinder's Assistant!


### Setup 

You need Racket, a LaTeX installation (TeXLive or MacTeX) and Sqlite3.

### Database

Publications are kept in the ```publication.rkt`` file. It's a simple
S-expression with a list of row vectors and a schema. The schema is there
to remind you what the columns mean. 

This file is read by Racket and the data is used to construct
an in-memory Sqlite3 database. Edit the ```publication.rkt``` file to
add more publications. You can load a different Racket file of publications
by setting the ```database-filename``` parameter like so:

```racket
(database-filename "my-other-publication.rkt")
```
The code words have to be unique. Otherwise the in-memory database
can't be created.


### User Interface and Parameters

All the functions that you are supposed to use and all the configurable
parameters are in the ```booky.rkt``` module. Require the module and
you are ready to work:

```racket
#lang racket

(require "booky.rkt")
```




### Example



