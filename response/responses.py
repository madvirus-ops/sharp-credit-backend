import sys

sys.path.append("./")


error_occured = {
    "success": False,
    "code": 400,
    "message": "Error occurred performing request",
}

invalid_phone = {
    "success": False,
    "code": 400,
    "message": "invalid phone number provided",
}
invalid_email = {
    "success": False,
    "code": 419,
    "message": "Invalid Email Address",
}

user_exist_phone = {
    "success": False,
    "code": 400,
    "message": "User with phone number already exists",
}
user_exist_email = {
    "success": False,
    "code": 419,
    "message": "User with email already exists",
}
user_notfound = {
    "success": False,
    "code": 404,
    "message": "User not found",
}
invalid_code = {"success": False, "code": 400, "message": "Invalid verification Code"}

code_expired = {"success": False, "code": 400, "message": "Verification Code expired"}
email_notverified = {"success": False, "code": 400, "message": "Email not verified"}
phone_notverified = {
    "success": False,
    "code": 400,
    "message": "Phone number not verified",
}
valid_code = {"success": True, "code": 200, "message": "Verification Code is Valid"}
otp_sent = {"success": True, "code": 200, "message": "OTP sent."}
pinset = {
    "success": True,
    "code": 201,
    "message": "transaction pin set",
}

passwordset = {
    "success": True,
    "code": 201,
    "message": "password set",
}

password_notset = {
    "success": False,
    "code": 400,
    "message": "password not set",
}

pin_notset = {"success": False, "code": 400, "message": "Pin not set"}


invalid_login = {
    "success": False,
    "code": 400,
    "message": "Invalid Username or password",
}

invalid_pin = {
    "success": False,
    "code": 400,
    "message": "Invalid Pin",
}



password_not_match = {
    "success": False,
    "code": 400,
    "message": "Invalid Old Password",
}


pin_not_match = {
    "success": False,
    "code": 400,
    "message": "Invalid Old Pin",
}

account_deactivated = {
    "success": True,
    "code": 200,
    "message": "Account Deleted Successfully",
}
