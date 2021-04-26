async function add_tab(tabId, tabUrl){
    var storage = window.localStorage;

    add_response = await fetch("http://flexr.org/api/tabs/", {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({url: tabUrl})

    })

    tab = await add_response.json();

    //bkg.console.log(tab);

    storage.setItem(tabId, tab.id)

}

async function remove_tab(tabId){
    var storage = window.localStorage;

    del_response = await fetch(`http://flexr.org/api/tab/${storage.getItem(tabId)}`, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        //body: JSON.stringify({id: storage.getItem(tabId)})

    })

    //tab = await del_response.json();

    storage.removeItem(tabId);



}

async function update_tab(tabId, tabUrl){

    await remove_tab(tabId);
    await add_tab(tabId, tabUrl);

    
}


chrome.webNavigation.onCompleted.addListener(function(details){
    var chromeTabs = []
    var storage = window.localStorage;

    if(storage.getItem('chromeTabs')){
        chromeTabs = JSON.parse(storage.getItem('chromeTabs'))
    }

    if(chromeTabs.includes(details.tabId)){
        console.log(details.tabId)
        console.log(details.url)
        //chrome.tabs.get(dteails.tabId, )
        update_tab(details.tabId, details.url)
    }
})


chrome.tabs.onRemoved.addListener(function(tabId){
    var chromeTabs = []
    var storage = window.localStorage;

    if(storage.getItem('chromeTabs')){
        chromeTabs = JSON.parse(storage.getItem('chromeTabs'))
    }

    if(chromeTabs.includes(tabId)){
        remove_tab(tabId)
    }

})

