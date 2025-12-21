class Dashboard {
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

            return {
                message: data.message,
                user_id: data.user_id,
                remember: data.remember
            }
        } catch(error) {
            return `error: ${error}`
        }
    }
}