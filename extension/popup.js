window.onload = function () {
    let loginButton = document.getElementById('loginButton');
    let siteButton = document.getElementById('siteButton');
    let bkg = chrome.extension.getBackgroundPage();
    let userid = -1;
    let accountid = -1;
    let accounts = [];
    

    loginButton.onclick = function(){
        var username = document.getElementById("username").Value;
        var password = document.getElementById("password").value;

        // this might error sometimes ......
        login.then(get_accounts).then(switch_account).then(to_menu_page);
    
    }

    siteButton.onclick = function(){
        window.open('http://127.0.0.1:8000', "_blank");
    }

    let login = new Promise(function(resolve, reject){
        var request = new XMLHttpRequest();
            
        request.open("POST", "http://127.0.0.1:8000/api/login/");
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        request.send("username=admin2&password=password");
        request.onload = () => {
            console.log(request);
            if (request.status == 200){
                bkg.console.log(JSON.parse(request.response));
                userid = JSON.parse(request.response).id
                
                resolve('Promise is resolved successfully.')

            }
            else{
                bkg.console.log(`error ${request.status} ${request.statusText}`);
                reject('Promise is rejected');  
            }
        }
    })
    
    function get_accounts(){
        bkg.console.log(userid)
        var request = new XMLHttpRequest();
        request.open("GET", "http://127.0.0.1:8000/api/accounts/")
        request.send()
        request.onload = () => {
            console.log(request);
            if (request.status == 200){
                bkg.console.log(JSON.parse(request.response));
                accounts = JSON.parse(request.response);
                accountid = accounts[0].account_id
                bkg.console.log(accountid)
                
            }
            else{
                bkg.console.log(`error ${request.status} ${request.statusText}`);
                return
                
            }
        }
    }
    
    function switch_account(){
        bkg.console.log(accountid)
        var request = new XMLHttpRequest();
        request.open("GET", `http://127.0.0.1:8000/api/account/${accountid}/switch/`)
        request.send()
        request.onload = () => {
            console.log(request);
            if (request.status == 200){
                bkg.console.log(JSON.parse(request.response));
                
            }
            else{
                bkg.console.log(`error ${request.status} ${request.statusText}`);
                return
                
            }
        }
    }

    function to_menu_page(){
        window.location.href = '/menu.html'
    }
    
}




// let changeColor = document.getElementById('changeColor');

// chrome.storage.sync.get('color', function(data) {
//   changeColor.style.backgroundColor = data.color;
//   changeColor.setAttribute('value', data.color);
// });

// changeColor.onclick = function(element) {
//     let color = element.target.value;
//     chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
//       chrome.tabs.executeScript(
//           tabs[0].id,
//           {code: 'document.body.style.backgroundColor = "' + color + '";'});
//     });
//   };