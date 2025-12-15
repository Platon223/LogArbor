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
                return `HTTP error while logging in into an account: ${response.status}, ${data.message}`
            }

            const data = await response.json()

            return `${data}`
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

    console.log(submit.message)

    if (submit.message.includes("user not found")) {
        alert(`User was not found`)
    } else if (submit.message.includes("invalid password")) {
        alert("Incorrect password provided")
    } else if (submit.message.includes("fetch for jwt")) {
        console.log("User remembered, fetch for jwt")
    } else if (submit.message.includes("verify")) {
        username.value = ""
        password.value = ""
        remember.value = ""

        localStorage.setItem("user_id", submit.user_id)
        localStorage.setItem("remember", submit.remember ? "True" : "False")

        window.location.href = "/auth/verify"
    } else {
        alert("Something went wrong.")
    }
})