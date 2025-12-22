class Dashboard {
    constructor(user_id) {
        this.user_id = user_id
    }


    async fetchCredentials() {

        try{
            const response = await fetch("/home/credentials/username", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return `HTTP error while logging in into an account: ${response.status}, ${data.message}`
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch(error) {
            return `error: ${error}`
        }
    }
}

async function main() {
    const dashboardClass = new Dashboard("123")
    const credentials = await dashboardClass.fetchCredentials()

    console.log(credentials.message)    
}