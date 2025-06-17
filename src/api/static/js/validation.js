export function validatePassword_logic(password) {
    if (password.length < 8) {
        return 1;
    }

    if (!(/[A-Z]/.test(password))) {
        return 2;
    }

    if (!(/[a-z]/.test(password))) {
        return 3;
    }

    if (!(/\d/.test(password))) {
        return 4;
    }

    return 0;
}

export function validateRepeat_logic(password, repeat) {
    return password == repeat;
}