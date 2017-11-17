var fs = require("fs");
casper = require("casper").create();

// var url = 'https://graph.facebook.com/v2.10/7126051465/posts?access_token=EAACEdEose0cBAFqxrBt1mEPdFxazVi4A48TI5WsZAkbMrrjeCdKvZBTbr8kZASGZCiqT3FeReOxhvJXjSXTh1LTfdX7ZCgWSZCIWELyljEmt3For4WkZAZC8VcaZBqLqhRoSEvC9YRfZABNLyV9T7hVsyDjvaZCOcX8tPZBVZAgtYwJngHYoPKqERNNufqkJy0UsAMZBoZD' 
var url = 'https://graph.facebook.com/v2.10/1191441824276882?fields=posts{reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBABZBN58NEYagRJQ3QWEYSkgsFduc6pqXkIZCwXodjLU5vFI864XVuZBwMjFzw5qqGf1hXWNkBypbj0YUSq3zDEWL9ANvGRNv0YZAoZC6f2ZA63mqYl6TGZByP7HCJsYKZCuBeMQ660pyHVuTQta4kV80XihJI1Ug5usWz8yM5ZCW2qLq6wsHxKPOxstm3E9K7WQZDZD&date_format=U'
var terminate = function() {
    this.echo("Exiting..").exit();
};


function getPosts() {
  // var data = $('html');
  var matches = []
  return matches    
}

function getRecentPosts(posts) {
  var now = new Date()
  var d = new Date(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 
    now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds(), now.getUTCMilliseconds());
  for (var i = 0, post; post = posts[i]; i++) {
    var post_time  = new Date(post["created_time"]*1000);
    var age = Math.abs(post_time - d)/28800000;
    if ((age < 24) && age > 23) {      
      fs.write('/Users/gabrielanthonygarza/Developer/archive/stancs/221/project/posts/' + post["from"]["name"] + '/' + post["id"] + '.txt', JSON.stringify(post), 'w');
    }
  }
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
  url = 'https://graph.facebook.com/v2.10/' + casper.cli.args[0] + '?fields=posts{reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBABZBN58NEYagRJQ3QWEYSkgsFduc6pqXkIZCwXodjLU5vFI864XVuZBwMjFzw5qqGf1hXWNkBypbj0YUSq3zDEWL9ANvGRNv0YZAoZC6f2ZA63mqYl6TGZByP7HCJsYKZCuBeMQ660pyHVuTQta4kV80XihJI1Ug5usWz8yM5ZCW2qLq6wsHxKPOxstm3E9K7WQZDZD&date_format=U'
}

casper.start().then(function() {
    this.open(url, {
        method: 'get',
        headers: {
            'Accept': 'application/json'
        }
    }).then(function() {
      //console.log('LOGGING')
    });
});
// casper.waitForSelector('pre', processPage, terminate)
var text = casper.evaluate(function(){
    return document.querySelector("*").innerText;
});
casper.run();
casper.on('load.started', function(resource) {
    // casper.echo(casper.getPageContent());
});

casper.on('resource.received', function(resource) {
  var data = casper.getPageContent();
  data = data.replace('<html><head></head><body></body></html>', "");
  data = data.replace('</pre></body></html>', "");
  data = data.replace('<pre><body><html>', "");  
  data = data.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', "");
  var jsonData = JSON.parse(data)["posts"]["data"]
  getRecentPosts(jsonData);
  var str = jsonData["id"] + ','
  str += jsonData["reactions_wow"]["summary"]["total_count"] + ','
  str += jsonData["reactions_love"]["summary"]["total_count"] + ','
  str += jsonData["reactions_haha"]["summary"]["total_count"] + ','
  str += jsonData["likes"]["summary"]["total_count"]
  // console.log(str)
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
