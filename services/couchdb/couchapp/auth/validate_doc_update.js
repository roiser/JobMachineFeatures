function(newDoc, oldDoc, userCtx) { 
  if (userCtx.roles.indexOf('_admin') !== -1) { 
    return; 
  } else { 
   throw({forbidden: 'read-only database'});
  } 
}
