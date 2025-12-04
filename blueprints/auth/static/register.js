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

        try{
            const response = await fetch("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(json)
            })

            if (!response.ok) {
                return `HTTP error while creating an account: ${response.status}`
            }

            const data = await response.json()

            return `${data.message}`
        } catch(error) {
            return `error: ${error}`
        }
    }
}

const formDiv = document.querySelector(".auth-form")
const username = document.getElementById("username")
const email = document.getElementById("email")
const password = document.getElementById("password")
const account_type = document.querySelector(".select-input")

formDiv.addEventListener("submit", (event) => {
    event.preventDefault()

    const registerClass = new Register(username.value, password.value, email.value, account_type.value)
    const submit = registerClass.submit()

    if (submit.includes("error")) {
        console.log("error occured")
    }
})