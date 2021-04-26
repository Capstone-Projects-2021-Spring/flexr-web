window.onload = function () {
    let tabsButton = document.getElementById('tabsButton');
    let bookmarksButton = document.getElementById('bookmarksButton');
    let accountsButton = document.getElementById('accountsButton');
    let siteButton = document.getElementById('siteButton');
    let logoutButton = document.getElementById('logoutButton');
    let bkg = chrome.extension.getBackgroundPage();

    async function logout(){
        let logout_response = await fetch('http://flexr.org/api/logout/',
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            //body: `username=${username}&password=${password}`

        });

        if (logout_response.status != 200){
            return 'error';
        }

        to_login_page()

        return 0;

    }

    siteButton.onclick = function(){
        window.open('http://flexr.org/', "_blank");
    }

    tabsButton.onclick = function(){
        window.location.href = '/tabs.html'
        
    }

    bookmarksButton.onclick = function(){
        window.location.href = '/bookmarks.html'
        
    }

    accountsButton.onclick = function(){
        window.location.href = '/accounts.html'
    }

    logoutButton.onclick = function(){
        logout()
    }

    function to_login_page(){
        window.location.href = '/popup.html';
    }
}