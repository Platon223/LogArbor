class Login {

    async submit(username, password) {
        const json = {
            username: username,
            password: password
        }

        try {
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

            return {
                message: data.message,
                user_id: data.user_id,
            }
        } catch (error) {
            return `error: ${error}`
        }
    }

    async fetchJWT(user_id) {
        const json = {
            user_id: user_id
        }

        try {
            const response = await fetch("/auth/jwt", {
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

            return {
                message: data.message
            }
        } catch (error) {
            return `error: ${error}`
        }
    }
}

const formDiv = document.querySelector(".auth-form")
const username = document.getElementById("username")
const password = document.getElementById("password")

formDiv.addEventListener("submit", async (event) => {
    event.preventDefault()

    const registerClass = new Login()
    const submit = await registerClass.submit(username.value, password.value)

    console.log(submit.message)

    if (submit.message.includes("user not found")) {
        alert(`User was not found`)
    } else if (submit.message.includes("invalid password")) {
        alert("Incorrect password provided")
    } else if (submit.message.includes("fetch for jwt")) {
        const fetchJwtResult = await registerClass.fetchJWT()

        if (fetchJwtResult.message.includes("send credentials")) {
            window.location.href = "/home/dashboard"
        } else {
            alert("Something went wrong. Please try again later.")
        }

    } else if (submit.message.includes("verify")) {
        username.value = ""
        password.value = ""

        localStorage.setItem("user_id", submit.user_id)
        localStorage.setItem("remember", submit.remember ? "True" : "False")

        window.location.href = "/auth/verify"
    } else {
        alert("Something went wrong.")
    }
})