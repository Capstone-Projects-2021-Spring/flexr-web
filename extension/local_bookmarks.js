window.onload = function () {
    let backButton = document.getElementById('backButton');
    let bkg = chrome.extension.getBackgroundPage();
    let chromeBookmarks = [];

    backButton.onclick = function() {
        window.location.href = '/menu.html'
    }

    async function add_bookmark(bookmarkUrl){
        bkg.console.log(bookmarkUrl);
        add_response = await fetch("http://18.221.147.115:8000/api/bookmarks/", {
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
                button = document.createElement('button');
                var text = document.createTextNode(bookmark.url);
                button.appendChild(text);
                
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

    // async function display_bookmarks(){
    //     await chrome.bookmarks.getTree(process_bookmark);
    //     bkg.console.log(chromeBookmarks.length);
    //     for(i = 0; i < chromeBookmarks.length; i++){
    //         bkg.console.log(chromeBookmarks[i].url);

    //         var parent = document.createElement('p');
    //         button = document.createElement('button');
    //         var text = document.createTextNode(chromeBookmarks[i].url);
    //         button.appendChild(text);
            
    //         bkg.console.log(chromeBookmarks[i].url)
    //         button.onclick = function(index){
                
    //             return function(){add_bookmark(chromeBookmarks[index].url)}
    //         }(i);

    //         parent.appendChild(button);
    //         document.body.appendChild(parent);
               
            
    //     }
    // }


    
    // display_bookmarks();

    chrome.bookmarks.getTree(process_bookmark);

}