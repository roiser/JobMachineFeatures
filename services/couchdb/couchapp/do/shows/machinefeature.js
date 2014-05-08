function getKeys(arr) {
  var keys=[];
  for (var key in arr) {
    if (arr.hasOwnProperty(key)) {
      keys.push(key);
    }
  }
  return keys;
}

function badRequest(txt) {
  return { code: 400,
           body: 'Bad request, ' + txt
         }
}

function txtValue(codeNum, val) {
  return { code: codeNum, 
           headers: { 'content-type': 'text/plain' },
           body: val
         }
}

function(doc, req) { 
  var keys = getKeys(req['query']);
  if (keys.length != 1) return badRequest('invalid number of GET parameters');
  var key0 = keys[0]; 
  if (req['query'][key0] != '') return badRequest('GET parameter must not have a value');
  if (key0[0] != '/') return badRequest('GET parameter needs to start with a forward slash');
  key0 = key0.slice(1);
  if (getKeys(doc['machinefeatures']).indexOf(key0) == -1) return txtValue(400, 'na')
  return txtValue(200, doc['machinefeatures'][key0].toString())
}
