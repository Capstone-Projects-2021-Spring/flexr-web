window.onload = function () {
    let backButton = document.getElementById('backButton');
    let trackButton = document.getElementById('trackButton');
    let bkg = chrome.extension.getBackgroundPage();
    let tabs = []

    storage = window.localStorage;

    if(storage.getItem('chromeTabs') == null){
        storage.setItem('chromeTabs', '[]')
    }
    
    backButton.onclick = function() {
        //storage.removeItem('chromeTabs');
        window.location.href = '/menu.html'
        
    }

    trackButton.onclick = function(){
        chrome.tabs.query({active: true, currentWindow: true}, function(T) {
            var activeTab = T[0];
            //bkg.console.log('test');
            //bkg.console.log(storage.getItem('chromeTabs'));


            var chromeTabs = []

            if(storage.getItem('chromeTabs') == ''){
                chromeTabs = []
            }
            else{
                chromeTabs = JSON.parse(storage.getItem('chromeTabs'));
            }

            if(!(chromeTabs.includes(activeTab.id))){
                chromeTabs.push(activeTab.id)
                add_tab(activeTab.id, activeTab.url)
            }


            storage.setItem('chromeTabs', JSON.stringify(chromeTabs));

            
      
            
            bkg.console.log(activeTab.url)
            bkg.console.log(activeTab.id)
            bkg.console.log(chromeTabs)
            bkg.console.log(storage.getItem('chromeTabs'));
       
         });

         
    }

    async function get_tabs(){
        tabs_response = await fetch("http://18.221.147.115:8000/api/tabs/");

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

    async function add_tab(tabId, tabUrl){
        var storage = window.localStorage;
    
        add_response = await fetch("http://18.221.147.115:8000/api/tabs/", {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({url: tabUrl})
    
        })

        tab = await add_response.json();

        bkg.console.log(tab);

        storage.setItem(tabId, tab.id)
    
    }
    

    get_tabs();
}