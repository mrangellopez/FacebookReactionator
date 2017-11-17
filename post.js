casper = require("casper").create()

// var url = 'https://graph.facebook.com/v2.10/7126051465/posts?access_token=EAACEdEose0cBAFqxrBt1mEPdFxazVi4A48TI5WsZAkbMrrjeCdKvZBTbr8kZASGZCiqT3FeReOxhvJXjSXTh1LTfdX7ZCgWSZCIWELyljEmt3For4WkZAZC8VcaZBqLqhRoSEvC9YRfZABNLyV9T7hVsyDjvaZCOcX8tPZBVZAgtYwJngHYoPKqERNNufqkJy0UsAMZBoZD' 
var url = 'https://graph.facebook.com/v2.10/10092511675?fields=posts{message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,likes.limit(0)}&access_token=EAACEdEose0cBAEyy62fhkDotUKxfxmL0Ux9ms2ocdcl7Yl3TRc4DWTZCGs1voRkCQK2qRqxRVjH1c9G82RRHeL0fPtyBKbaeTsmZBCRDXMwZCgVnv0JzhGIutarLAwtDQuvzd3ZBZB99uoqKsv64wqngtIDacbL6Fd15TCvauxWl2dIJa4vugPJ2hbIbI7B8ZD'
var terminate = function() {
    this.echo("Exiting..").exit();
};

//https://graph.facebook.com/v2.10/10092511675?fields=posts{message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBAJcpZANp0oZCfq27p0vkTMSQDGtUqEBHHMgNNQaBvcPNyEOpqZCIP1xXSnZBcQRc46eiGO8ThYlZCXu7EoFDqgnazlm0fWGjDlokZBlZB0Ovk1jDaHpPdySuZAYbMlTieZB7xWR651it9V1cJp1N6WM0XQeb51grVN8uifZAJE06ZBbhMd0DbkrbhsZD
//https://graph.facebook.com/v2.10/10092511675?fields=posts{message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBALmULqteqzR1LyZCjDZCre7DTZAeGiaKi1WLYUbBZCxSPkJOjXAyofZAy98HA5IrGZBYmso8vSXhZBKgEea3ldjBz79XygbtovZCuDR5ywCGNWvMkl5VZBaG47bOA0FOymyDcR7Cx5j0CaS9qnXOXEHrIJvcFxOsAxQ6QIX7GGpq1upghPiuPSisZD

function getPosts() {
  // var data = $('html');
  var matches = []
  return matches    
}
//maybe delete the first wrod in the date here in the processing -- find space and go to following d=iz
var processPage = function() {
  console.log('asdasd');
  matches = this.evaluate(getPosts);
  console.log('{ "games" : ')
  require('utils').dump(matches);
  console.log('}')
} 

if (casper.cli.options.inline) {
  url = 'https://graph.facebook.com/v2.10/' + casper.cli.args[0] + '?fields=reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)&access_token=EAACEdEose0cBAEyy62fhkDotUKxfxmL0Ux9ms2ocdcl7Yl3TRc4DWTZCGs1voRkCQK2qRqxRVjH1c9G82RRHeL0fPtyBKbaeTsmZBCRDXMwZCgVnv0JzhGIutarLAwtDQuvzd3ZBZB99uoqKsv64wqngtIDacbL6Fd15TCvauxWl2dIJa4vugPJ2hbIbI7B8ZD'
}

function getRecentPosts(posts) {
  var now = new Date()
  var d = new Date(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 
    now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds(), now.getUTCMilliseconds());
}

casper.start().then(function() {
    this.open(url, {
        method: 'get',
        headers: {
            'Accept': 'application/json'
        }
    }).then(function() {
      // console.log('LOGGING')
    });
});
// casper.waitForSelector('pre', processPage, terminate)
var text = casper.evaluate(function(){
    return document.querySelector("*").innerText;
});
casper.run();
// casper.echo(text);
casper.on('load.started', function(resource) {
    // casper.echo(casper.getPageContent());
});

casper.on('resource.received', function(resource) {
  var data = casper.getPageContent();
  data = data.replace('</pre></body></html>', "");
  data = data.replace('<pre><body><html>', "");  
  data = data.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', "");
  var jsonData = JSON.parse(data)
  // for (var i = 0; i < jsonData.length; i++) {
  //   console.log(jsonData[i]["id"]);
  // }
  // console.log(jsonData["reactions_sad"]["summary"]["total_count"])
  var str = jsonData["id"] + ','
  str += jsonData["reactions_wow"]["summary"]["total_count"] + ','
  str += jsonData["reactions_love"]["summary"]["total_count"] + ','
  str += jsonData["reactions_haha"]["summary"]["total_count"] + ','
  str += jsonData["likes"]["summary"]["total_count"]
  console.log(str)
  // console.log(JSON.parse(data)["posts"]["data"][0]["reactions_sad"]["summary"]["total_count"]);
});



// casper.run(function() {
//   data = JSON.parse(this.getPageContent());
//   for (var i = 0, post; post = data['data'][i]; i++) {
//       require('utils').dump(post["id"])
//   }
//   this.exit();
// });
// casper.waitForSelector('pre', processPage, terminate)
