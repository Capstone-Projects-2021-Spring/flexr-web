window.onload = function () {
    let backButton = document.getElementById('backButton');
    let bkg = chrome.extension.getBackgroundPage();
    let tabs = []
    
    backButton.onclick = function() {
        window.location.href = '/menu.html'
    }

    let get_tabs = new Promise(function(resolve, reject){
        var request = new XMLHttpRequest();
            
        request.open("GET", "http://127.0.0.1:8000/api/tabs/");
        //request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        //request.send("username=admin2&password=password");
        request.send();
        request.onload = () => {
            console.log(request);
            if (request.status == 200){
                bkg.console.log(JSON.parse(request.response));
                //userid = JSON.parse(request.response).id
                tabs = JSON.parse(request.response)
                
                resolve('Promise is resolved successfully.')

            }
            else{
                bkg.console.log(`error ${request.status} ${request.statusText}`);
                reject('Promise is rejected');  
            }
        }
    })

    get_tabs.then(display_tabs)


    function display_tabs(){

        for(i = 0; i < tabs.length; i++){
            bkg.console.log(tabs[i].url);

            var parent = document.createElement('p');
            var a = document.createElement('a');
            var linkText = document.createTextNode(tabs[i].url);
            a.appendChild(linkText);
            a.href = tabs[i].url;

            parent.appendChild(a);
            document.body.appendChild(parent);
        }

        

    }
}