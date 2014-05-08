function(doc, req) { 
  log(req); 
  return { 'code': 200, 
           'headers': { 'content-type': 'text/plain' }, 
            body: doc['jobfeatures'][req.query.name].toString() 
  } 
}
