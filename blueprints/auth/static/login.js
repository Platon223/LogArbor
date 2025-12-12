class Login {
    constructor(username, password, remember) {
        this.username = username
        this.password = password
        this.remember = remember
        
    }


    async submit() {
        const json = {
            username: this.username,
            password: this.password,
            remember: this.remember
        }

        try{
            const response = await fetch("/auth/login", {
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
const password = document.getElementById("password")
const remember = document.getElementById("remember")

formDiv.addEventListener("submit", async (event) => {
    event.preventDefault()

    let remember_data = false

    if (remember.checked) {
        remember_data = true
    } else {
        remember_data = false
    }

    const registerClass = new Login(username.value, password.value, remember_data)
    const submit = await registerClass.submit()

    if (submit.includes("username is already taken")) {
        alert(`Username: ${username.value} is already taken. Please choose another one.`)
    } else if (submit.includes("errorwhile")) {
        alert("Something went wrong on our end. Please try again in 24 hours.")
    } else if (submit.includes("errorwith")) {
        alert("Something went wrong on our end. Please try again in 24 hours.")
    } else if (submit.includes("{'password")) {
        alert("Password has to be at least 6 characters long.")
    } else if (submit.includes("verify")) {
        username.value = ""
        password.value = ""

        window.location.href = "/auth/verify"
    } else {
        alert("Something went wrong.")
    }
})