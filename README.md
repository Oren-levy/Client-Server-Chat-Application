### A BRIEF DESCRIPTION OF THE APPLICATION
The application specified in this report is an online videoconferencing and messaging application.

The application is based on a client-server model consisting of one server and multiple clients communicating concurrently.

For the messaging system, the client and server communicate using TCP to guarantee reliability, in-order delivery, and the potential for congestion control (although congestion control is not currently implemented in this application, it may be done later as the application grows and will be discussed as a potential improvement later).

The server makes use of multi-threading, generating a new thread for each respective client to service any number of clients exclusively and without interruption.

Further, the videoconferencing aspect of the application supports peer-to-peer file exchange and is done using UDP for low latency. Clients communicate with each other without the need of the server.

In addition to simple messaging, the application supports other features relevant to such a system and will be explained in the application functions section.

DESIGN AND TRADE-OFFS AND MESSAGE FORMATTING
The program was designed as a utility concept, and as a result, there are no frivolous features offered to the users.

It is written in Python 3.7. The application is controlled from a command line interface, where the user inputs their messages to be written to the message.log file.

There is no fancy design. For the most part, it is a lightweight and low storage design application with an emphasis on reliability, hence the application layer protocol implementing a TCP transport protocol.

In contrast, UDP is used for the peer-to-peer file exchange aspect of the application as less reliability is needed with video streaming and some data may be lost in transit in favor of lower latency.

With respect to formatting, all messages are encoded as a JSON object. JSON objects rely on key-value pairings. The application relies on the json.loads() method to convert a string into a JSON object, and json.dumps() that converts a JSON object into a string. This is consistent amongst the client and the server, as the server expects to receive a JSON object and so does the client. In this fashion the client and server communicate with each other; encoding and decoding JSON objects.

The benefit of using JSON objects is they are very easy to parse, with no additional bytes sent. Losing data loses only a single object which is easily re-transmitted. However, the disadvantage is if the application were to grow it is not very scalable. If a client were to send many large JSON objects, the three-packet TCP handshake would increase latency. However, the application is intended as a utility concept and so does not need to consider such things.

Sure, here is the formatted text for Github Editor:


## HOW THE SYSTEM WORKS: COMMANDS, FUNCTIONS, MEANING

The system is actioned over a command line terminal. It is a multithreaded application such that the server creates a new thread for each respective client, one to receive messages and one to send messages. Data structures include classes and lists of dictionaries to store, maintain, and update information.

### Authentication

* Username and password authentication by the server.
* The server will block a client for ten seconds if too many login attempts with a valid username but invalid password occurs.

### Messaging

* Clients can send the server a message which will update a message.log file in the server.
* Messages from clients will be appended to the message.log file in the order they have been received.
* The message.log file has remained consistent with the specification and is in the form:

```
Messagenumber; timestamp; username; message; edited or unedited
```

with the time stamp being of the form DD MMM YYYY hh:mm:ss.

* Issue the message command: `MSG message`
* For example: `MSG Hellow World`

### Deleting

* Messages may be deleted from the server by the user who issued the message.
* This will remove the message from the message.log file and re-order the remaining messages.
* Issue the delete command: `DLT messagenumber timestamp`
* For example: `DLT #1 08 Apr 2021 13:59:19`

### Editing

* Messages may be edited from the server by the user who issued the message.
* This will completely replace the original message with the new message and update the message.log file to show `<edited>`.
* Issue the edit command: `EDT messagenumber timestamp message`
* For example: `EDT #1 08 Apr 2021 13:59:19 Hello`

### Read Messages

* A request from the user to read all messages in the message.log file AFTER a specified time.
* Issue the read message command: `RDM timestamp`
* For example: `RDM 08 Apr 2021 13:59:19`

### Active Users

* A request from the client to the server to report the users that are currently accessing the server.
* Issue the active user command: `ATU`
* For example: `ATU`

### Logout

* A request to both the client and the server to terminate all active threads, and exit the system.
* The server will likewise update the user.log file to represent those users that are logged in.
* Issue the logout command: `OUT`
* For example: `OUT`

### Upload File

* A request by a user to establish a private connection with another user.
* This is a peer-to-peer (client-to-client) connection that bypasses the need for a TCP server, and instead implements a UDP connection.
* Issue the file exchange between two clients command: `UPD username filename`
* For example: `UPD Yoda video.mp4`

### POSSIBLE IMPROVEMENTS AND EXTENSIONS
This application has been designed as a utility concept and so may be improved by way of security,
congestion control, more reliable transfer of peer-to-peer data, JSON data scalability, and direct
messaging between clients. To start, there is no security design, users may send harmful data to the
server without it being checked. A security measure should be implemented to check for mal-data.
Additionally, by similar vein, there is no congestion control implementation on the peer-to-peer or
server side, which invited possible DDOS attacks, as the server may be overwhelmed my messages
from a particular client. As such, it is recommended some congestion control framework, such as
TCP Tahoe or Reno be implemented. Further, JSON is effective with small data transfer, however, if a
client were to send many large Json objects, the three-packet TCP handshake would increase latency
slowing down the server. Finally, the server should support direct live messaging between users as
currently users can not speak to each other directly or privately but instead download the
message.log file.
