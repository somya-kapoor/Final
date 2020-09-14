const express = require('express');
const app = express();
const server = app.listen(3000, console.log("Socket.io Hello Wolrd server started!"));
const io = require('socket.io')(server);



io.sockets.on('connection', function(socket) {
    function publishRoomReaderCount(room) {
        var room_var  = io.sockets.adapter.rooms[room];
        var broadcast_name = 'reader-count-'+room;
        console.log("Broadcasting " + room_var.length + " to " + broadcast_name);
        io.emit(broadcast_name, room_var.length)
     } 
    socket.on('room', function(room) {
        console.log("joining " + room);
        socket.join(room);
        publishRoomReaderCount(room);
    });
    
    socket.on('disconnect', function() {
        console.log('Got disconnect!');
        Object.keys(io.sockets.adapter.rooms).forEach(function(roomName){
            publishRoomReaderCount(roomName);
        });

     });
    
});


// // now, it's easy to send a message to just the clients in a given room
// room = "room1";
// io.sockets.in(room).emit('message', 'what is going on, party people?');

// // this message will NOT go to the client defined above
// io.sockets.in('foobar').emit('message', 'anyone in this room yet?');
// io.on('connection', (socket) => {
//     //console.log("Client connected!");
//     socket.on('message-from-client-to-server', (msg) => {
//         console.log(msg);
//     })
//     socket.emit('message-from-server-to-client', room.length);
// });



// io.sockets.on('connection', function(client){
//     var Room = "";
//     client.on("setNickAndRoom", function(nick, fn){
//         client.join(nick.room);
//         Room = nick.room;
//         client.broadcast.to(Room).emit('count', "Connected:" + " " + count);
//         fn({msg :"Connected:" + " " + count});
//     });