// netcat.js -- a simple telnet client
//
// > node netcat.js irc.freenode.net 6667

var net = require('net'),
    sys = require('sys'),
    argv = process.argv;

if (argv.length != 4) {
    sys.puts('usage: ' + argv[0] + ' ' + argv[1] + ' HOST PORT');
    process.exit(1);
}

(function(host, port) {
     var name = host + ':' + port,
         client = net.createConnection(port, host);

     client.addListener('connect', function() {
         var input = process.openStdin(),
             output = process.stdout;

         sys.puts('Connected to ' + name + '; use ^C to exit.');

         input.addListener('data', function(chunk) {
             client.write(chunk);
         });

         client.addListener('data', function(chunk) {
             output.write(chunk);
         });

         client.addListener('close', function() {
             sys.puts('Connection to ' + name + ' closed.');
             process.exit(0);
         });
    });
}).apply(this, argv.slice(2));
