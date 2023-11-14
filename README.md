# Librarian Dron

"Librarian Dron" is a dron that manages your books and bookshelves.  
It consists of three parts: Drone Controller, Book Database, User Interface.

## Drone Controller

The "Drone Controller" is a program that controls the drone.  
It is written in Python and runs on Raspberry Pi or Arduino.(Not decided yet)  
It flies around the room and scans books on the bookshelf.  
This will add books to the database.  

Whenever someone wants to lend a book, just notify the drone controller.  
The drone will fly to the bookshelf and bring the book to the user.  
When the user returns the book, the drone will return the book to the bookshelf.

## Book Database

The "Book Database" is a database that stores information about books and bookshelves.  
It stores all the books in the bookshelf and the location of the books.  
If a book is lent, it will be marked as "lent" in the database.  

## User Interface

A "User Interface" is a simple dashboard that allows you to search for books and manage your bookshelf.
It's a simple web application written in Python and Flask.  