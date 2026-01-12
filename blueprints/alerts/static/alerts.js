class Alerts {



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

    async fetchAlerts() {
        try{
            const response = await fetch("/api/v1/alerts/alerts", {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while getting alerts: ${response.status}, ${data.message}`
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

    async markAsViewed(alert_id) {
        try{
            const markAsViewedJson = {
                alert_id: alert_id,
                status: true
            }
            const response = await fetch("/api/v1/alerts/marked_viewed", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(markAsViewedJson)
            })

            if (!response.ok) {
                const data = await response.json()
                alert(`HTTP error while marking an alert as viewed: ${response.status}, ${data.message}`)
            }

            const data = await response.json()

            if (data.message.includes("alert not found")) {
                alert("Alert was not found. Please try again later.")
            } else if(data.message.includes("something went wrong")) {
                window.location.href = "/auth/login"
            } else if (data.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (data.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (data.message.includes("marked as viewed")) {
                window.location.reload()    
            }
        } catch(error) {
            alert("Something went wrong while marking your alert as viewed. Please try again later.")
        }
    }

    async deleteAlert(alert_id) {
        try{
            const markAsViewedJson = {
                alert_id: alert_id
            }
            const response = await fetch("/api/v1/alerts/alerts", {
                method: "DELETE",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(markAsViewedJson)
            })

            if (!response.ok) {
                const data = await response.json()
                alert(`HTTP error while deleting an alert: ${response.status}, ${data.message}`)
            }

            const data = await response.json()

            if (data.message.includes("alert not found")) {
                alert("Alert was not found. Please try again later.")
            } else if(data.message.includes("something went wrong")) {
                window.location.href = "/auth/login"
            } else if (data.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (data.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (data.message.includes("deleted")) {
                window.location.reload()    
            }
        } catch(error) {
            alert("Something went wrong while deleting an alert. Please try again later.")
        }
    }
}

async function main() {
    const alertsClass = new Alerts()
    const credentials = await alertsClass.fetchCredentials()

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

    const allAlerts = await alertsClass.fetchAlerts()

    if (Array.isArray(allAlerts.message)) {
        const alertsContent = allAlerts.message.map((element) => {
            return `
                <div class="alert-line ${element.viewed ? 'viewed' : 'unread'} ${element.level}">
                    <span class="alert-dot ${element.viewed ? 'viewed' : ''}"></span>
                    <span class="time">${element.time}</span>
                    <span class="level">${element.level}</span>
                    <span class="message">
                        ${element.message} <strong>(${element.service_name})</strong>
                    </span>
                    <div class="alert-actions">
                        ${element.viewed 
                            ? `<button onclick="alertsClass.deleteAlert('${element.id}')" class="btn small danger">Delete</button>` 
                            : `<button onclick="alertsClass.markAsViewed('${element.id}')" class="btn small">Mark Viewed</button><button class="btn small danger">Delete</button>`
                        }
                    </div>
                </div>`
        }).join('')

        document.getElementById("alerts-container").innerHTML = alertsContent
    } else if (allAlerts.message.includes("no alerts")) {
        document.getElementById("alerts-container").innerHTML = `<h4>No Alerts Yet, <a href='/docs/sending-logs'>Learn More</a></h4>`
    } else if(allAlerts.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (allAlerts.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (allAlerts.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    }
}

main()