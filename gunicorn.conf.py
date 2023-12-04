# Server socket
#   bind - The socket to bind.
bind = "10.0.0.209:8080"
#   backlog - The number of pending connections. This refers
#       to the number of clients that can be waiting to be
#       served. 
backlog = 64

# Worker processes
#
#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
workers = 1