window.onload = function () {
    let backButton = document.getElementById('backButton');
    let bkg = chrome.extension.getBackgroundPage();
    let bookmarks = []
    
    backButton.onclick = function() {
        window.location.href = '/menu.html'
    }

    async function get_bookmarks(){
        bookmarks_response = await fetch("http://127.0.0.1:8000/api/bookmarks/");

        bookmarks = await bookmarks_response.json();

        display_bookmarks();
    }

    function display_bookmarks(){

        for(i = 0; i < bookmarks.length; i++){
            bkg.console.log(bookmarks[i].url);

            var parent = document.createElement('p');
            var a = document.createElement('a');
            var linkText = document.createTextNode(bookmarks[i].url);
            a.appendChild(linkText);
            a.href = bookmarks[i].url;

            parent.appendChild(a);
            document.body.appendChild(parent);
        }

    }

    get_bookmarks();
}