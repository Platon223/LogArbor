class Verify {
    constructor(code, user_id, remember) {
        this.code = code
        this.user_id = user_id
        this.remember = remember
        
    }


    async submit() {
        const json = {
            code: this.code,
            user_id: this.user_id,
            remember: this.remember
        }

        try{
            const response = await fetch("/auth/verify", {
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
const code = document.getElementById("code")
const user_id = localStorage.getItem("user_id")
const remember = localStorage.getItem("remember")

formDiv.addEventListener("submit", async (event) => {
    event.preventDefault()

    const verifyClass = new Verify(code.value, user_id, remember === "True" ? true : false)
    const submit = await verifyClass.submit()

    console.log(submit)

    if (submit.includes("invalid code")) {
        alert(`Invalid code provided.`)
    } else if (submit.includes("expired")) {
        alert("The code has been epired.")
    } else if (submit.includes("success")) {
        code.value = ""

        window.location.href = "/home/dashboard"
    } else {
        alert("Something went wrong.")
    }
})