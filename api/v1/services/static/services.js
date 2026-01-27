class Services {


    async fetchCredentials() {

        try{
            const response = await fetch("/api/v1/home/credentials/username", {
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

    async allServices() {
        try{
            const response = await fetch("/api/v1/services/all_services", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while fetching all of the services: ${response.status}, ${data.message}`
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

    async newService(name, url, alert_level) {
        const createNewServiceJSON = {
            name: name,
            url: url,
            alert_level: alert_level
        }
        try{
            const response = await fetch("/api/v1/services/create", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(createNewServiceJSON)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while creating a new service: ${response.status}, ${data.message}`
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

const createButton = document.getElementById("create-button")
const newServiceForm = document.querySelector(".modal-form")
const modal = document.getElementById("serviceModal");

newServiceForm.addEventListener("submit", async (event) => {
    event.preventDefault()

    const nameValue = document.getElementById("name")
    const urlValue = document.getElementById("url")
    const alertLevelValue = document.getElementById("level")

    const dashboardClass = new Services()
    const createNewService = await dashboardClass.newService(nameValue.value, urlValue.value, alertLevelValue.value)

    if (!createNewService.message.includes("created")) {
        alert("Something went wrong.")
    }

    nameValue.value = ""
    urlValue.value = ""
    alertLevelValue.value = ""

    modal.style.display = "none"

    window.location.reload()
})

document.getElementById("openServiceModal").onclick = () => {
    modal.style.display = "flex";
};
document.getElementById("closeServiceModal").onclick = () => {
    modal.style.display = "none";
};
window.onclick = e => {
    if (e.target === modal) modal.style.display = "none";
};

async function main() {
    const servicesClass = new Services()
    const credentials = await servicesClass.fetchCredentials()

    if (credentials.message.includes("user not found")) {
        window.location.href = "/auth/register"
    } else if(credentials.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else {
        document.querySelector(".env").innerHTML = `<a href='/settings'>${credentials.message}</a>`    
    }

    const all_services = await servicesClass.allServices()

    if (all_services.message.includes("no services")) {
        document.querySelector(".services-grid").innerHTML = "No Services Yet"
    } else if (Array.isArray(all_services.message)) {
        all_services.message.forEach(element => {
            document.querySelector(".services-grid").innerHTML += `<div onclick="window.location.href = '/services/${element.id}' " class="service-card online">
                <div class="terminal-header">
                    <span>${element.name}</span>
                    <span class="terminal-dot green"></span>
                </div>

                <div class="service-body">
                    <p><strong>Status:</strong> Healthy</p>
                    <p><strong>Logs:</strong> 123</p>
                    <p><strong>Url:</strong> ${element.url}</p>
                    <p><strong>Alert Level:</strong> ${element.alert_level}</p>
                </div>

                <div class="service-actions">
                    <a href="/logs/auth_service" class="btn primary small">View Logs</a>
                </div>
            </div>`
        });
    } else if(credentials.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (credentials.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else {
        window.location.href = "/auth/login"
    }
}

main()