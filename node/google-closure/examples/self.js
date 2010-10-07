var fs = require('fs'),
    closure = require('../lib/closure'),
    self = fs.readFileSync(__filename);

closure.compile(self, function(err, code) {
  if (err) throw err;

  var smaller = Math.round((1 - (code.length / self.length)) * 100);
  console.log('Myself, compiled (%d% smaller)', smaller);
  console.dir(code);
});