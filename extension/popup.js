window.onload = function () {
    let loginButton = document.getElementById('loginButton');
    let siteButton = document.getElementById('siteButton');
    let bkg = chrome.extension.getBackgroundPage();
    let userid = -1;
    let accountid = -1;
    let accounts = [];

    async function login(){
        let login_response = await fetch('http://127.0.0.1:8000/api/login/',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'username=admin2&password=password'
        });

        if (login_response.status != 200){
            return 'error';
        }

        user = await login_response.json();

        


        let accounts_response = await fetch('http://127.0.0.1:8000/api/accounts/',
        {
            method: 'GET'
        })

        if (accounts_response.status != 200){
            return 'error';
        }

        accounts = await accounts_response.json();

        //bkg.console.log(accounts);

        accountid = accounts[0].account_id;


        let switch_response = await fetch(`http://127.0.0.1:8000/api/account/${accountid}/switch/`,
        {
            method: 'GET'
        })

        if (switch_response.status != 200){
            return 'error';
        }

        to_menu_page();


        return 0;


    }

    async function check_status(){
        let status_response = await fetch('http://127.0.0.1:8000/api/status/',
        {
            method: 'GET',
            
        });

        if (status_response.status != 200){
            return 'error';
        }

        status = await status_response.json();

        if(!status){
            return 'not logged in';
        }

        
        


        let accounts_response = await fetch('http://127.0.0.1:8000/api/accounts/',
        {
            method: 'GET'
        })

        if (accounts_response.status != 200){
            return 'error';
        }

        accounts = await accounts_response.json();

        //bkg.console.log(accounts);

        accountid = accounts[0].account_id;


        let switch_response = await fetch(`http://127.0.0.1:8000/api/account/${accountid}/switch/`,
        {
            method: 'GET'
        })

        if (switch_response.status != 200){
            return 'error';
        }

        to_menu_page();


        return 0;


    }

    check_status();
    
    


    loginButton.onclick = function(){
        var username = document.getElementById("username").Value;
        var password = document.getElementById("password").value;

        result = login();
        bkg.console.log(result);
    
    }

    siteButton.onclick = function(){
        window.open('http://127.0.0.1:8000', "_blank");
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