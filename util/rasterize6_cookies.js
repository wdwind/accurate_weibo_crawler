// As explained here: http://code.google.com/p/phantomjs/wiki/QuickStart

var page = new WebPage(), address, output, size;
//console.log('Usage: rasterize.js URL filename');

var args = require('system').args;

//var chinese_fonts = ['Microsoft yahei', 'Droid Sans Fallback', "宋体", "方正韵动中黑简体", "方正兰亭黑简体", "方正兰亭中黑_GBK", ".萍方-简"]

var cookies = phantom.addCookie({
  'name': 'SUB',
  'domain': '.weibo.cn',
  'value': args[4],
  'path': '/'
});
// if (cookies){
//     console.log('Load cookies successfully!')
// };

address = args[1];
output = args[2];
page.viewportSize = {width: 880, height: 600};
page.zoomFactor = 2;
page.open(address, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        console.log('Page loading status: ' + status);
        window.setInterval(function() {
            page.evaluate(function() {
              // Scrolls to the bottom of page
              window.document.body.scrollTop = document.body.scrollHeight;
            });
        }, 10000);
        
        window.setTimeout(function () {
            font = "'Helvetica','\\u65B9\\u6B63\\u5170\\u4EAD\\u4E2D\\u9ED1_GBK','Microsoft yahei','Segoe UI Symbol'";
            page.evaluate(function (font) {
                var r = /\\u([\d\w]{4})/gi;
                font = font.replace(r, function (match, grp) {
                        return String.fromCharCode(parseInt(grp, 16));});
                font = unescape(font);
                document.body.style["fontFamily"]=font;
            }, font);

            page.render(output);
            phantom.exit();
        }, args[3]);
    }
});