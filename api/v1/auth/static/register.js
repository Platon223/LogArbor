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
                const data = await response.json()
                return `HTTP error while creating an account: ${response.status}, ${data.message}`
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

formDiv.addEventListener("submit", async (event) => {
    event.preventDefault()

    const registerClass = new Register(username.value, password.value, email.value, account_type.value)
    const submit = await registerClass.submit()

    if (submit.includes("username is already taken")) {
        alert(`Username: ${username.value} is already taken. Please choose another one.`)
    } else if (submit.includes("errorwhile")) {
        alert("Something went wrong on our end. Please try again in 24 hours.")
    } else if (submit.includes("errorwith")) {
        alert("Something went wrong on our end. Please try again in 24 hours.")
    } else if (submit.includes("{'password")) {
        alert("Password has to be at least 6 characters long.")
    } else if (submit.includes("created")) {
        username.value = ""
        email.value = ""
        password.value = ""
        account_type.value = ""

        window.location.href = "/auth/login"
    } else {
        alert("Something went wrong.")
    }
})