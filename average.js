var fs = require("fs");
casper = require("casper").create();

var url = 'https://graph.facebook.com/v2.10/117533210756?fields=posts{reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),from,reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBAN3SAgJOL2lYfelvXtAYg8EVEqgsvPJWTdq0oMrhgiyoyjwTwrKEhd5p7PKYlYZAVRWfXmK6HZAwJTYVLaL6QUjHZAQKMOd1gbpODNTG8sZCuobHrZCn5ZA8mhgeOwZCCtfkMTbUOItJ4WgUCeokkGEHHHflh3NTv8qrCpPoaPrbAwOC3In2kkZD&date_format=U'

function getAverageReactions(posts) {
  averages = {'likes': 0, 'sad': 0, 'wow': 0, 'haha': 0, 'angry': 0, 'love': 0}
  for (var i = 0; i < posts.length; i++) {
    averages['likes'] += posts[i]['likes']['summary']['total_count']
    averages['sad'] += posts[i]['reactions_sad']['summary']['total_count']
    averages['wow'] += posts[i]['reactions_wow']['summary']['total_count']
    averages['haha'] += posts[i]['reactions_haha']['summary']['total_count']
    averages['angry'] += posts[i]['reactions_angry']['summary']['total_count']
    averages['love'] += posts[i]['reactions_love']['summary']['total_count']
  }
  for (var avg in averages) {
    averages[avg] = averages[avg] / posts.length
  }
  fs.write('/Users/gabrielanthonygarza/Developer/archive/stancs/221/project/posts/' + posts[0]["from"]["name"] + '/averages.txt', JSON.stringify(averages), 'w');
  // fs.write('/Users/gabrielanthonygarza/Developer/archive/stancs/221/project/averages.txt', JSON.stringify(posts), 'w');
}

if (casper.cli.options.inline) {
  url = 'https://graph.facebook.com/v2.10/' + casper.cli.args[0] + '?fields=posts{reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),from,reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),likes.limit(0).summary(total_count)}&access_token=EAACEdEose0cBAN3SAgJOL2lYfelvXtAYg8EVEqgsvPJWTdq0oMrhgiyoyjwTwrKEhd5p7PKYlYZAVRWfXmK6HZAwJTYVLaL6QUjHZAQKMOd1gbpODNTG8sZCuobHrZCn5ZA8mhgeOwZCCtfkMTbUOItJ4WgUCeokkGEHHHflh3NTv8qrCpPoaPrbAwOC3In2kkZD&date_format=U'
}

casper.start().then(function() {
  this.open(url, {
      method: 'get',
      headers: {
          'Accept': 'application/json'
      }
  }).then(function() {});
});

var text = casper.evaluate(function(){
    return document.querySelector("*").innerText;
});

casper.run();
casper.on('load.started', function(resource) {});
casper.on('resource.received', function(resource) {
  var data = casper.getPageContent();
  data = data.replace('<html><head></head><body></body></html>', "");
  data = data.replace('</pre></body></html>', "");
  data = data.replace('<pre><body><html>', "");  
  data = data.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', "");
  var jsonData = JSON.parse(data)["posts"]["data"]
  getAverageReactions(jsonData);
});
