window.onload = function () {
    let tabsButton = document.getElementById('tabsButton');
    let bookmarksButton = document.getElementById('bookmarksButton');
    let siteButton = document.getElementById('siteButton');
    let logoutButton = document.getElementById('logoutButton');
    let bkg = chrome.extension.getBackgroundPage();

    siteButton.onclick = function(){
        window.open('http://127.0.0.1:8000', "_blank");
    }

    tabsButton.onclick = function(){
        window.location.href = '/tabs.html'
        
    }

    bookmarksButton.onclick = function(){
        window.location.href = '/bookmarks.html'
        
    }

    logoutButton.onclick = function(){
        
    }
}