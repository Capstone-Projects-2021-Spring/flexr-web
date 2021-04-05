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
        let logout =  new Promise(function(resolve, reject){
            var request = new XMLHttpRequest();
                
            request.open("GET", "http://127.0.0.1:8000/api/logout/");
            //request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            //request.send("username=admin2&password=password");
            request.send();
            request.onload = () => {
                console.log(request);
                if (request.status == 200){
                    bkg.console.log(JSON.parse(request.response));
                    //userid = JSON.parse(request.response).id
                    r = JSON.parse(request.response)
                    
                    resolve('Promise is resolved successfully.')
    
                }
                else{
                    bkg.console.log(`error ${request.status} ${request.statusText}`);
                    reject('Promise is rejected');  
                }
            }
        });

        logout.then(to_login_page);
        
    }

    function to_login_page(){
        window.location.href = '/popup.html';
    }
}