# Booky the bookbinder's Assistant!

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


### Database


### Configuration


### Searches

Change into the ```sample-project``` directory to try these out.

Get compact list of publications. 

```$ python -m booky --list```

Get a list of publications with all the bookbinding data.

```$ python -m booky --list-full

Check if key is available:

```$ python -m booky --check-key coma

Search keys. If you use wildcards, you must enclose the expression in quotes.

```$ python -m booky --search-keys coma```
```$ python -m booky --search-keys "c*"```

Search titles. Enclose expressions in quotes if you use wildcards.

```$ python -m booky --search-titles "*theo*"

Wildcard searches of keys and titles are case-insensitive.

### Tickets



