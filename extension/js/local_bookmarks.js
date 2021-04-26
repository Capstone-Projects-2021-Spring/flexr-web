window.onload = function () {
    let backButton = document.getElementById('backButton');
    let bkg = chrome.extension.getBackgroundPage();
    let chromeBookmarks = [];

    backButton.onclick = function() {
        window.location.href = '/menu.html'
    }

    async function add_bookmark(bookmarkUrl){
        bkg.console.log(bookmarkUrl);
        add_response = await fetch("http://flexr.org/api/bookmarks/", {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({url: bookmarkUrl})
    })

    }

    //stolen from stackoverflow
    function process_bookmark(bookmarks) {
        for (var i =0; i < bookmarks.length; i++) {
            var bookmark = bookmarks[i];
            if (bookmark.url) {
                bkg.console.log("bookmark: "+ bookmark.title + " ~  " + bookmark.url);

                chromeBookmarks.push(bookmark)

                var parent = document.createElement('p');
                button = document.createElement('img');
                button.setAttribute('src', 'icons/plus.png');
                button.setAttribute('width', '20px');
                button.setAttribute('class','plus_icon');
                button.style.cursor = "pointer";


                var text = document.createTextNode(bookmark.url);
                parent.appendChild(text);
                
                bkg.console.log(bookmark.url)
                button.onclick = function(url){
                    return function(){add_bookmark(url)}
                }(bookmark.url);
    
                parent.appendChild(button);
                document.body.appendChild(parent);

            }
    
            if (bookmark.children) {
                process_bookmark(bookmark.children);
            }
        }
    }

    chrome.bookmarks.getTree(process_bookmark);

}