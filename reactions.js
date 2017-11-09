casper = require("casper").create()

var url = 'https://graph.facebook.com/v2.10/7126051465/posts?access_token=EAACEdEose0cBAFfEVHfZCU6p5mUo7R0e2gqUnswA3Xx4T6FmHKxp1pLCWEYTc74QI8ygXjfAQhccAZC6jzrVXP1SGzw4dqSI5uvUBaXoO1vpnlKEXbuW4czX6KIXXSj3ebkQnq5wyPt1B9RnZACfSxDcEHu3J1z6dm9ruNkRF5HY6DX4xQ9tMi4jSaZB8A8ZD' 
// var url = 'https://graph.facebook.com/v2.10/1191441824276882?fields=posts{reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBAMXZCfdZCAnwA2X0N5thyHRIAKVEI4BGQnrZA6169I9hWRk0Ii8mI8tPNx0OwXYoUiIXpVZBTgHssBzU5bKuTvisv2lIGTfqXJTwcOyx9Ka6CRpOGALIWc4bXPNZC6skkZBB0tXDSiLZBRsocLidrXqOhrZBjMQbivBDIkiZAqJDWM6UrZBZAVSqToZD'
var terminate = function() {
    this.echo("Exiting..").exit();
};


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
  url = 'https://graph.facebook.com/v2.10/' + casper.cli.args[0] + '?fields=posts{reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),message,source,status_type,picture,object_id,name,parent_id,properties,type,to,from,created_time,permalink_url,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBAMXZCfdZCAnwA2X0N5thyHRIAKVEI4BGQnrZA6169I9hWRk0Ii8mI8tPNx0OwXYoUiIXpVZBTgHssBzU5bKuTvisv2lIGTfqXJTwcOyx9Ka6CRpOGALIWc4bXPNZC6skkZBB0tXDSiLZBRsocLidrXqOhrZBjMQbivBDIkiZAqJDWM6UrZBZAVSqToZD'
}
casper.start().then(function() {
    this.open(url, {
        method: 'get',
        headers: {
            'Accept': 'application/json'
        }
    }).then(function() {
      console.log('LOGGING')
    });
});
// casper.waitForSelector('pre', processPage, terminate)
var text = casper.evaluate(function(){
    return document.querySelector("*").innerText;
});
casper.echo(text);
casper.run();
casper.echo(text);
casper.on('load.started', function(resource) {
    casper.echo(casper.getPageContent());
});

casper.on('resource.received', function(resource) {
  var data = casper.getPageContent();
  data = data.replace('</pre></body></html>', "");
  data = data.replace('<pre><body><html>', "");  
  data = data.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', "");
  var jsonData = JSON.parse(data)["posts"]["data"]
  for (var i = 0; i < jsonData.length; i++) {
    console.log(jsonData[i]["id"]);
  }
  console.log(JSON.parse(data)["posts"]["data"][0]["reactions_sad"]["summary"]["total_count"]);
});



// casper.run(function() {
//   data = JSON.parse(this.getPageContent());
//   for (var i = 0, post; post = data['data'][i]; i++) {
//       require('utils').dump(post["id"])
//   }
//   this.exit();
// });
// casper.waitForSelector('pre', processPage, terminate)
