class Register {
    constructor(username, password, email, account_type) {
        this.username = username
        this.password = password
        this.email = email
        this.account_type = account_type
    }


    async submit() {
        const json = {
            username: this.username,
            password: this.password,
            email: this.email,
            account_type: this.account_type
        }


        const response = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(json)
        })
    }
}