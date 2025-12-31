class Logs {



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

    async fetchLogs() {
        try{
            const response = await fetch("/logs/all_logs", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while getting logs of your services: ${response.status}, ${data.message}`
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
    const logsClass = new Logs()
    const credentials = await logsClass.fetchCredentials()

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

    const logs = await logsClass.fetchLogs()


    if (Array.isArray(logs.message)) {
        let servicesLogsContent = ""


        logs.message.forEach(element => {
            servicesLogsContent += `<section class="terminal">
                <div class="terminal-header">
                    <span>${element.service_name}</span>
                    <span class="terminal-dot green"></span>
                </div>

                <div class="terminal-body">
                    ${element.logs.length === 0 ? `No Logs Yet` : element.logs.map(logElement => `
                        <div class="log-line ${logElement.level}">
                            <span class="time">${logElement.time}</span>
                            <span class="level">${logElement.level}</span>
                            <span class="message">${logElement.message}</span>
                        </div>
                    `).join('')}
                </div>

                <div class="terminal-toolbar">
                    <input
                        type="text"
                        class="log-search"
                        placeholder="Search logs..."
                    >

                    <div class="log-filters">
                        <button class="filter-btn active" data-level="all">ALL</button>
                        <button class="filter-btn info" data-level="info">INFO</button>
                        <button class="filter-btn warn" data-level="warn">WARN</button>
                        <button class="filter-btn error" data-level="error">ERROR</button>
                    </div>

                    <button class="clear-btn">Clear</button>
                </div>

            </section>`
        })

        document.getElementById("terminalServicesWrapper").innerHTML = servicesLogsContent
    } else if(logs.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (logs.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (logs.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else if (logs.message.includes("no services")) {
        document.getElementById("terminalServicesWrapper").innerHTML = "No Services Yet"  
    }
}

main()