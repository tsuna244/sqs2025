// pokemon search function
function onSearch() {
    $("#search_btn").prop("disabled", true);
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
        $("#search_btn").prop("disabled", false);
    });
}

// login function
function send() {
    $("#login_btn").prop("disabled", true);
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
            document.loginform.username.value = ""
            document.loginform.password.value = ""
            $("#modalMessage").text("Username or Password wrong")
            $("#popupModal").modal()
            $("#login_btn").prop("disabled", false);
        }
    })
    .catch(error => {
        console.error(error);
    });
}

// registration function
function send_registration() {
    $("#register_btn").prop("disabled", true);
    let username =  document.loginform.username.value;
    let password = document.loginform.password.value;
    let repeat_passwd = document.loginform.password_repeat.value;
    let fail = false;
    if (!validatePassword_logic(password)) {
        fail = true;
        $("#modalMessage").text("Password validation failed");
        $("#popupModal").modal();
    }
    if (!validateRepeat_logic(password, repeat_passwd)) {
        fail = true;
        $("#modalMessage").text("Repeated password must be same");
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
            document.loginform.username.value = "";
            document.loginform.password.value = "";
            document.loginform.password_repeat.value = "";
            $("#modalMessage").text(data["details"]);
            $("#popupModal").modal();
            if(data["details"].includes("successfully")) {
                location.href="/login";
            }
        })
    }
    $("#register_btn").prop("disabled", false);
}

// validation function for password repeat
function validateRepeat(repeat_passwd) {
    let passwd = $("#password").val();
    let check = validateRepeat_logic(passwd, repeat_passwd)
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

}

// authentication (inside the navbar and webpages)
function authenticate_navbar() {
    let token = window.sessionStorage.token
    if (typeof token == "undefined" || token == "null") return;
    let current_token = JSON.parse(token);
    if (typeof current_token != "undefined" && current_token != "null") {
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

// authentication for content
function authenticate_content() {
    let token = window.sessionStorage.token
    if (typeof token == "undefined" || token == "null") location.href = "/unauth";
    let current_token = JSON.parse(token);
    if (typeof current_token != "undefined" && current_token != "null") {
        const headers = { 'Authorization': current_token["token_type"] + " " + current_token["access_token"] }; // auth header with bearer token
        fetch("/get_user", { 
            method: "POST",
            headers: headers 
        })
        .then(response => response.json())
        .then(data => {
                if (!data.hasOwnProperty("user_name")) {
                    location.href="/unauth";
                }
            }
        )
    }else
        location.href = "/unauth";
}

// functions for deck!!!
function create_dropdown_element_for_user(selection_id, deck_ids) {
    let html_str = "";
    for(let value of deck_ids) {
        let poke_id = value["_id"];
        let poke_name = value["_name"];
        html_str += `<li><a class="d-menu-item-${selection_id} dropdown-item" data-value="${poke_name}-${poke_id}" href="#">${poke_name}</a></li>` + "\n";
    }
    let selection_list = "#selection-list-" + selection_id;
    $(selection_list).html(html_str);
}

function add_click_event_to_selection(selection_id) {
    const menu_selection_val = ".d-menu-item-" + selection_id;
    const btn_selection_val = "d-menu-btn-" + selection_id;
    const dropdownItems = document.querySelectorAll(menu_selection_val);
  const dropdownButton = document.getElementById(btn_selection_val);

  dropdownItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault(); // Prevent the link from navigating
      const selectedValue = item.getAttribute('data-value');
      dropdownButton.textContent = selectedValue.split("-")[0];
      const selection_html_id = "#selection-" + selection_id;
      fetch("/Pokemon_Id/" + selectedValue.split("-")[1], { 
            method: "POST",
        })
        .then(response => response.json())
        .then(data => {
                const html_str = `<img src="/static/${data["pokemon_sprite_path"]}">Points: <span id="poke-points-${selection_id}">${data["pokemon_points"]}</span>`
                $(selection_html_id).html(html_str);
            }
        )
    });
  });
}

function calc_and_update_points() {
    $("#save_points_btn").prop("disabled", true);
    let points_sum = 0;
    for (let i = 1; i < 7; i++) {
        let val = $(`#poke-points-${i}`).text();
        points_sum += parseInt(val);
    }

    let token = window.sessionStorage.token
    if (typeof token == "undefined" || token == "null") location.href = "/unauth";
    let current_token = JSON.parse(token);
    if (typeof current_token != "undefined" && current_token != "null") {
        const headers = { 'Authorization': current_token["token_type"] + " " + current_token["access_token"] }; // auth header with bearer token
        fetch("/get_user", { 
            method: "POST",
            headers: headers 
        })
        .then(response => response.json())
        .then(data => {
                if (data.hasOwnProperty("user_name")) {
                    const user_name = data["user_name"]
                    update_points(user_name, points_sum);
                }else {
                    $("#modalMessage").text("Could not get user. Adding Pokemon to deck failed!")
                    $("#popupModal").modal()
                }
                $("#save_points_btn").prop("disabled", false);
            }
        )
    }
}

function update_points(user_name, points_elem) {
     fetch("/update_points", { 
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: user_name, points_elem: points_elem})
    })
    .then(response => response.json())
    .then(data => {
            $("#modalMessage").text(data["details"])
            $("#popupModal").modal()
        }
    )
}

function create_deck_page() {
    let token = window.sessionStorage.token
    if (typeof token == "undefined" || token == "null") location.href = "/unauth";
    let current_token = JSON.parse(token);
    if (typeof current_token != "undefined" && current_token != "null") {
        const headers = { 'Authorization': current_token["token_type"] + " " + current_token["access_token"] }; // auth header with bearer token
        fetch("/get_user", { 
            method: "POST",
            headers: headers 
        })
        .then(response => response.json())
        .then(data => {
                if (data.hasOwnProperty("user_name")) {
                    console.log(data["deck_ids"]);
                    for(let i = 1; i < 7; i++) {
                        create_dropdown_element_for_user(`${i}`, data["deck_ids"]);
                        add_click_event_to_selection(`${i}`);
                    }
                }
            }
        )
    }
}

function get_random_pokemon_by_gen_id(generation_id) {
    const gen_btns = $(".gen_selection");
    gen_btns.each(function () {
      $(this).prop('disabled', true);
    });
    $("#loading_pack").text("Loading Pokemon")
    fetch("/Pokemon_Rand/" + generation_id, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
            if (data.hasOwnProperty("pokemon_id")) {
                // add pokemon to user (update_user)
                let result_field = $("#poke_result")
                result_field.html(`<span>${data["pokemon_name"]}: ${data["pokemon_points"]} Points</span><img src="/static/${data["pokemon_sprite_path"]}">`)
                add_rand_poke_to_user({_id: data["pokemon_id"], _name: data["pokemon_name"]});
            }
            gen_btns.each(function () {
            $(this).prop('disabled', false);
            });
        }
    )
    
}

function add_rand_poke_to_user(new_elem) {
    let token = window.sessionStorage.token
    if (typeof token == "undefined" || token == "null") location.href = "/unauth";
    let current_token = JSON.parse(token);
    if (typeof current_token != "undefined" && current_token != "null") {
        const headers = { 'Authorization': current_token["token_type"] + " " + current_token["access_token"] }; // auth header with bearer token
        fetch("/get_user", { 
            method: "POST",
            headers: headers 
        })
        .then(response => response.json())
        .then(data => {
                if (data.hasOwnProperty("user_name")) {
                    const user_name = data["user_name"]
                    update_user(user_name, new_elem);
                }else {
                    $("#modalMessage").text("Could not get user. Adding Pokemon to deck failed!")
                    $("#popupModal").modal()
                }
            }
        )
    }
}

function update_user(user_name, new_elem) {
    fetch("/add_to_deck", { 
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: user_name, new_elem: new_elem})
    })
    .then(response => response.json())
    .then(data => {
            $("#modalMessage").text(data["details"])
            $("#popupModal").modal()
        }
    )
}

function update_leaderboard() {
    $("#update_lb_btn").prop("disabled", true);
    fetch("/get_users", { 
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
            console.log(data);
            if (data.hasOwnProperty("users")) {
                let l = data["users"].length;
                if (l > 10) l = 10;
                let html_str = ""
                for (let i = 0; i < l; i++) {
                    html_str += `<li>${data["users"][i]["user_name"]} : ${data["users"][i]["points"]}</li> \n`;
                }
                $("#user_list").html(html_str);
            }else {
                $("#user_list").text("No users found");
            }
            $("#update_lb_btn").prop("disabled", false);
        }
    )
}