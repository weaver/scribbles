var sys = require('sys');

exports.compile = compile;

function compile(code, next) {
  try {
    var qs = require('querystring'),
        http = require('http'),
        host = 'closure-compiler.appspot.com',
        body = qs.stringify({
          js_code: code.toString('utf-8'),
          compilation_level: 'ADVANCED_OPTIMIZATIONS',
          output_format: 'json',
          output_info: 'compiled_code'
        }),
        client = http.createClient(80, host).on('error', next),
        req = client.request('POST', '/compile', {
          'Host': host,
          'Content-Length': body.length,
          'Content-Type': 'application/x-www-form-urlencoded'
        });

    req.on('error', next).end(body);

    req.on('response', function(res) {
      if (res.statusCode != 200)
        next(new Error('Unexpected HTTP response: ' + res.statusCode));
      else
        capture(res, 'utf-8', parseResponse);
    });

    function parseResponse(err, data) {
      err ? next(err) : loadJSON(data, function(err, obj) {
        var error;
        if (err)
          next(err);
        else if ((error = obj.errors || obj.serverErrors || obj.warnings))
          next(new Error('Failed to compile: ' + sys.inspect(error)));
        else
          next(null, obj.compiledCode);
      });
    }
  } catch (err) {
    next(err);
  }
}

function capture(input, encoding, next) {
  var buffer = '';

  input.on('data', function(chunk) {
    buffer += chunk.toString(encoding);
  });

  input.on('end', function() {
    next(null, buffer);
  });

  input.on('error', next);
}

function loadJSON(data, next) {
  var err, obj;

  try {
    obj = JSON.parse(data);
  } catch (x) {
    err = x;
  }
  next(err, obj);
}
