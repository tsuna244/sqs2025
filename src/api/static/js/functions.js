// pokemon search function
function onSearch() {
    let loading_elem = $("#loading");
    loading_elem.text("Loading");
    let pokemon_elem = $("#poke_elem");
    $("#poke_elem").hide();
    const serach_value = $("#search_input").val();
    fetch("/Pokemon_Name/" + serach_value, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.hasOwnProperty("pokemon_id")) {
            $("#poke_id").text(data["pokemon_id"]);
            $("#poke_name").text(data["pokemon_name"]);
            $("#poke_gen").text(data["pokemon_generation"]);
            $("#poke_rarity").text(data["pokemon_rarity"]);
            let pokemon_stats = data["pokemon_stats"];
            $("#poke_hp").text(pokemon_stats[0]["stat_value"]);
            $("#poke_atk").text(pokemon_stats[1]["stat_value"]);
            $("#poke_def").text(pokemon_stats[2]["stat_value"]);
            $("#poke_satk").text(pokemon_stats[3]["stat_value"]);
            $("#poke_sdef").text(pokemon_stats[4]["stat_value"]);
            $("#poke_spd").text(pokemon_stats[5]["stat_value"]);
            
            $("#poke_sprite").html(`<img src="/static/${data["pokemon_sprite_path"]}" alt="Pokemon Sprite not found" width=300 height=300>`);

            pokemon_elem.show();
            loading_elem.text("");
        }else {
            loading_elem.text("Pokemon not found!");
            pokemon_elem.hide();
        }

    });
}

// login function
function send() {
    let formData = new FormData();
    formData.append("username", document.loginform.username.value);
    formData.append("password", document.loginform.password.value);

    fetch('/token', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => { // data is a JSON object
        if (data.hasOwnProperty("access_token")) {
            window.sessionStorage.token = JSON.stringify(data);
            document.location.href = "/";
        }
        else {
            console.log(JSON.stringify(data));
        }
    })
    .catch(error => {
        console.error(error);
    });
}

// registration function
function send_registration() {
    let username =  document.loginform.username.value;
    let password = document.loginform.password.value;
    let repeat_passwd = document.loginform.password_repeat.value;
    let fail = false;
    if (!validatePassword(password)) {
        fail = true;
        $("#modalMessage").text("Password validation failed");
        $("#popupModal").modal();
    }else if (!validateRepeat(repeat_passwd)) {
        $("#modalMessage").text("Password was repeated incorrectly");
        $("#popupModal").modal();
    }
    let regExp = /[a-z]/i;
    if (!regExp.test(username.charAt(0))) {
        fail = true;
        $("#modalMessage").text("Username must start with a letter");
        $("#popupModal").modal();
    }

    if (!fail) {
        
        fetch('/register_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username: username, password: password}),
        })
        .then(response => response.json())
        .then(data => { // data is a JSON object
            console.log(JSON.stringify(data));
        })
    }

}

// validation function for password repeat
function validateRepeat(repeat_passwd) {
    let passwd = $("#password").val();
    let check = repeat_passwd === passwd;
    let err_message = $("#repeatMessage");
    if (check) {
        err_message.text('Same password');
        err_message.removeClass("text-danger");
        err_message.addClass("text-success");
    }else {
        err_message.text('Does not equal password');
        err_message.removeClass("text-success");
        err_message.addClass("text-danger");
    }
    return check;
}

function set_passwd_class(element, success) {
    if (success) {
        element.removeClass("bi-x-lg");
        element.addClass("bi-check-lg");
        element.addClass("text-success");
        element.removeClass("text-danger");
    }else {
        element.addClass("bi-x-lg");
        element.removeClass("bi-check-lg");
        element.removeClass("text-success");
        element.addClass("text-danger");
    }
}

// validation function for password input
function validatePassword(password) {
    const elem_len = $("#length");
    const elem_upper = $("#capital");
    const elem_digit = $("#number");
    const elem_lower = $("#letter");

    let fail = false;

    if (password.length >= 8) {
        set_passwd_class(elem_len, true);
    }else {
        fail = true;
        set_passwd_class(elem_len, false);
    }

    if (/[A-Z]/.test(password)) {
        set_passwd_class(elem_upper, true);
    }else {
        fail = true;
        set_passwd_class(elem_upper, false);
    }

    if (/[a-z]/.test(password)) {
        set_passwd_class(elem_lower, true);
    }else {
        fail = true;
        set_passwd_class(elem_lower, false);
    }

    if (/\d/.test(password)) {
        set_passwd_class(elem_digit, true);
    }else {
        fail = true;
        set_passwd_class(elem_digit, false);
    }

    const errorMessage = $('errorMessage');

    if (fail) {
        errorMessage.text('Weak Password');
        errorMessage.removeClass('text-success');
        errorMessage.addClass('text-danger');
    }else {
        errorMessage.text('Strong Password');
        errorMessage.removeClass('text-danger');
        errorMessage.addClass('text-success');
    }

    return !fail;

}

// authentication (inside the navbar and webpages)
function authenticate_navbar() {
    let token = window.sessionStorage.token
    if (token == "undefined" || token == "null") return;
    let current_token = JSON.parse(token);
    if (current_token != "undefined" || current_token != "null") {

        const headers = { 'Authorization': current_token["token_type"] + " " + current_token["access_token"] }; // auth header with bearer token
        fetch("/get_user", { 
            method: "POST",
            headers: headers 
        })
        .then(response => response.json())
        .then(data => {
                if (data.hasOwnProperty('user_name')) {
                    let html = `<span class="navbar-text mr-2">${data["user_name"]}</span>
                        <button class="btn btn-outline-success" type="button" onclick="logout()">Logout</button>
                        `;
                    $('#login_register').html(html);

                    $('#pack').removeClass('disabled');
                    $('#pack').attr('href', '/pack_opening');
                    $('#deck').removeClass('disabled');
                    $('#deck').attr('href', '/my_deck');
                }
            }
        )
    }
}

// logout function
function logout() {
    window.sessionStorage.token = "null"
    window.location.href = "/"
}