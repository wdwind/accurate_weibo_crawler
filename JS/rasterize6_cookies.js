// As explained here: http://code.google.com/p/phantomjs/wiki/QuickStart

var page = new WebPage(), address, output, size;
//console.log('Usage: rasterize.js URL filename');

var args = require('system').args;

// console.log(args[0]);
// console.log(args[1]);
// console.log(args[2]);
// console.log(args[3]);
// console.log(args[4]);

//var chinese_fonts = ['Microsoft yahei', 'Droid Sans Fallback', "宋体", "方正韵动中黑简体", "方正兰亭黑简体", "方正兰亭中黑_GBK", ".萍方-简"]
font = "'Helvetica','\\u65B9\\u6B63\\u5170\\u4EAD\\u4E2D\\u9ED1_GBK','Microsoft yahei','Segoe UI Symbol'";

var cookies = phantom.addCookie({
  'name': 'SUB',
  'domain': '.weibo.cn',
  'value': args[4],
  'path': '/'
});

address = args[1];
output = args[2];
page.viewportSize = {width: 880, height: 600};
page.zoomFactor = 2;

// http://phantomjs.org/api/webpage/handler/on-resource-requested.html
// page.onResourceRequested = function(requestData, networkRequest) {
//   //console.log('Request (#' + requestData.id + '): ' + JSON.stringify(requestData));
//   console.log(requestData.url);
//   if (requestData.url.indexOf('comment') != -1) {
//     //networkRequest.abort();
//     networkRequest.changeUrl("");
//   }
// };

page.open(address, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        console.log('Page loading status: ' + status);
        if (address.indexOf("comment") != -1) {
          window.setInterval(function() {
              page.evaluate(function() {
                // Scrolls to the bottom of page
                window.document.body.scrollTop = document.body.scrollHeight;
              });
          }, 10000);
        }
        
        window.setTimeout(function () {
            page.evaluate(function (font) {
                var r = /\\u([\d\w]{4})/gi;
                font = font.replace(r, function (match, grp) {
                        return String.fromCharCode(parseInt(grp, 16));});
                font = unescape(font);
                document.body.style["fontFamily"]=font;
            }, font);

            // page.evaluate(function() {
            //   var cmtTab = document.querySelectorAll('[cont-type="cmtTab"]')[0];
            //   if (cmtTab != null) {
            //     var ul = cmtTab.getElementsByTagName('ul');
            //     if (ul != null && ul.length > 1) {
            //         //ul[1].parentNode.removeChild(ul[1]);
            //         //ul[1].remove();
            //         ul[1].setAttribute('style', 'display:none');
            //     }
            //   }

            //   var cmtTab = document.querySelectorAll('[data-node-type="comment-list"]')[0];
            //   if (cmtTab != null) {
            //     var sec = cmtTab.getElementsByTagName('section');
            //     if (sec != null && sec.length > 1) {
            //         //sec[1].parentNode.removeChild(sec[1]);
            //         //sec[1].remove();
            //         sec[1].setAttribute('style', 'display:none');
            //     }
            //   }
            // });

            if (address.indexOf("comment") == -1) {
              var clipRect = page.evaluate(function(){
                var m1 = document.getElementsByClassName("module-infobox line-bottom more");
                if (m1.length != 0) return m1[0].getBoundingClientRect();

                var m2 = document.getElementsByClassName("commment-more");
                if (m2.length != 0) return m2[0].getBoundingClientRect();

                var m3 = document.getElementsByClassName("comment-more");
                if (m3.length != 0) return m3[0].getBoundingClientRect();

                return null;
              });

              if (clipRect != null) {
                page.clipRect = {
                  top: 0,
                  left: 0,
                  width: page.viewportSize['width'],
                  height: clipRect.top*page.zoomFactor + clipRect.height*page.zoomFactor*2
                };
              }
            }

            page.render(output);
            phantom.exit();
        }, args[3]);
    }
});