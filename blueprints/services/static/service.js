class Service {


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
                return {
                    message: `HTTP error while getting username of your account: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch(error) {
            return `error: ${error}`
        }
    }

    async fetchSettings() {
        try{

            const service_json = {
                "service_id": service_id
            }


            const response = await fetch("/services/service", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(service_json)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while getting settings of your service: ${response.status}, ${data.message}`
                }
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
    const serviceClass = new Service()
    const credentials = await serviceClass.fetchCredentials()

    if (credentials.message.includes("user not found")) {
        window.location.href = "/auth/register"
    } else if(credentials.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else {
        document.querySelector(".env").innerHTML = credentials.message    
    }

    const settings = await serviceClass.fetchSettings()

    if (settings.message instanceof Object) {
        document.getElementById("serviceNameField").value = settings.message.name
        document.getElementById("serviceIdField").value = settings.message.id
        document.getElementById("serviceUrlField").value = settings.message.url
        document.getElementById("serviceAlertLevelField").value = settings.message.alert_level
    } else if(credentials.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("service not found")) {
        window.location.href = "/services/"
    } else {
        window.location.href = "/services/"
    }
}

main()
