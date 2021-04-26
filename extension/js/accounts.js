window.onload = function () {
    let backButton = document.getElementById('backButton');
    let bkg = chrome.extension.getBackgroundPage();
    let accounts = []
    
    backButton.onclick = function() {
        window.location.href = '/menu.html'
    }

    async function get_accounts(){
        accounts_response = await fetch('http://flexr.org/api/accounts/');

        accounts = await accounts_response.json();

        display_accounts();
    }

    async function switch_account(accountid){
        let switch_response = await fetch(`http://flexr.org/api/account/${accountid}/switch/`);

        if(switch_response.ok){
            bkg.console.log('switched to account with account id:' + accountid);
        }
        else{
            bkg.console.log('error');
        }
    }


    function display_accounts(){
        for(i = 0; i < accounts.length; i++){
            bkg.console.log(accounts[i].username + ' ' + accounts[i].account_id);

            var parent = document.createElement('p');
            button = document.createElement('button');
            var text = document.createTextNode(accounts[i].username);
            button.style.cursor = "pointer";
            button.appendChild(text);
            
            
            button.onclick = function(index){
                return function(){switch_account(accounts[index].account_id)}
            }(i);

            parent.appendChild(button);
            document.body.appendChild(parent);
               
            
        }
    
    }

    get_accounts();
}