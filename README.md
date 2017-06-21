# rent-a-slogan

The idea behind this project is to try event loops in
languages/libraries I find interesting at the moment.

All solutions will solve the following problem -

* Create a client-server that is completely asynchronous
and evented.
* Clients can connect to the server on a socket
* Clients can add a slogan
* Clients can rent a slogan for 15 seconds
* Clients can ask for status of rental system
(total slogans, number of slogans rented, number of connected clients etc)

## Example

```bash
$ nc localhost 25001
status
Total number of slogans: 10
Number of rents: 2
Number of connected clients: 3

add::Just do it
Just do it
add::Just do it
error: slogan already exists

rent
OK: id:4 title:t1
Slogan id 4 has expired
```
