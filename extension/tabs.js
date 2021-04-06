window.onload = function () {
    let backButton = document.getElementById('backButton');
    let trackButton = document.getElementById('trackButton');
    let bkg = chrome.extension.getBackgroundPage();
    let tabs = []
    
    backButton.onclick = function() {
        window.location.href = '/menu.html'
    }

    trackButton.onclick = function(){
        chrome.tabs.query({active: true, currentWindow: true}, function(T) {
            var activeTab = T[0];
            

            bkg.console.log(activeTab.url)
            bkg.console.log(activeTab.id)
       
         });
    }

    async function get_tabs(){
        tabs_response = await fetch("http://127.0.0.1:8000/api/tabs/");

        tabs = await tabs_response.json();

        display_tabs();
    }

    function display_tabs(){

        for(i = 0; i < tabs.length; i++){
            //bkg.console.log(tabs[i].url);

            var parent = document.createElement('p');
            var a = document.createElement('a');
            var linkText = document.createTextNode(tabs[i].url);
            a.appendChild(linkText);
            a.href = tabs[i].url;

            parent.appendChild(a);
            document.body.appendChild(parent);
        }


    }

    get_tabs();
}