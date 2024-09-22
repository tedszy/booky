# booky the Bookbinder's Assistant!

### Intro

A stack of editions of the same publication are cut to standard dimensions
and arranged into volumes. The standard dimensions and the thickness 
of the volume determines the the dimensions of the book-binding components.
Bookbinding jobs are summarized by tickets. One publication, several
volumes. The user supplies a code for the publication, the volume
thickness, and the title to put on the volume. Booky looks up the
data on that publication by the given code, then computes binding
component dimensions, and arranges everything into a nice looking 
ticket-like table. 

### Setup 

You need Racket, a LaTeX installation (TeXLive or MacTeX) and Sqlite3.

### Database

Publications are kept in the ```publication.rkt``` file. It's a simple
Racket expression with a list of row vectors and a schema. The schema 
is there to remind you what the columns mean. The file is read by Racket 
and the data is used to construct an in-memory Sqlite3 database. 
Edit the ```publication.rkt``` file to add more publications. 
You can load a different Racket file of publications
by setting the ```database-filename``` parameter like so:

```racket
(database-filename "my-other-publication.rkt")
```
The code words have to be unique. Otherwise the in-memory database
can't be created.

### User Parameters

All the functions that you are supposed to use and all the configurable
parameters are in the ```booky.rkt``` module. Require the module and
you are ready to work:

```racket
#lang racket

(require "booky.rkt")
```
The following parameters can be adjusted by the user. 
**All measurement dimensions are in millimeters!**

* ```publication-filename.``` This is set to ```publication.rkt``` but 
can have any number of databases and set this name to whichever you want
to work with.

* ```upper-margin``` and ```lower-margin.``` White space at top and 
bottom of page. Defaults are 5 both.

* ```left-margin``` and ```right-margin.``` White space on left
and right edges of page. Defaults are 2 both.

* ```font-size.``` Default value is 11 points.

* ```vertical-stretch.``` Currently set to 1.2. If you want vertically
tighter looking tickets, set this to 1.1 or 1.0.

* ```title-width.``` Width of the box containing the publication title.
Default is 26 millimeters.

* ```title-styling.``` Default title size is ```"\\large".``` 
You can make it bigger with ```"\\Large".``` Other things are possible
if you know LaTeX.


* ```label-width.``` Width of the column containing the 
binding component label names. Default is 18 millimeters.

* ```volume-separation.``` This is extra separation between the
volume column-pairs within a ticket. Default is 0.

* ```ticket-spacing.``` How much vertical space do you want between
tickets? The default is 4 millimeters.

* ```cardboard-label```, ```paper-label```, ```buckram-label```, 
  ```backcard-label``` are currently set to French labels. 
  You can set them to English labels like so:
  
```racket
(cardboard-label "cardboard")
(paper-label "paper")
(buckram-label "buckram")
(backcard-label "backcard")
```

* ```pdflatex-program.``` Currently set to ```pdflatex,``` but if your
OS has trouble finding the executable, you can solve that by simply
putting a name with a full path.


Racket parameters are like functions. You can see the value of
a parameter by calling it in the REPL. For example, let's see
the ticket spacing:

```racket
> (ticket-spacing)
4
```

And we change the ticket spacing to 6 millimeters like so:

```racket
(ticket-spacing 6)
```

All the other parameters work the same way. Just make sure you set
parameters before you start the database and before you run 
the ```pdf``` function. So it's best to set parameters right after
you do ```(require "booky.rkt").```


### User interface

         volume
         make-ticket-new 
         make-ticket
         pdf
         start
         find

### Example



