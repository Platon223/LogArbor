class Dashboard {



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
            return {message: `error: ${error}`}
        }
    }

    async fetchMetrics() {

        try{
            const response = await fetch("/api/v1/logs/metrics", {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while getting metrics of your services: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch(error) {
            return {message: `error: ${error}`}
        }
    }
}

async function main() {
    const dashboardClass = new Dashboard()
    const credentials = await dashboardClass.fetchCredentials()

    console.log(credentials.message)

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

    const metrics = await dashboardClass.fetchMetrics()

    console.log(metrics)

    const dates = []

    metrics.forEach(service => {
        if (service.logs_metrics[1]) {
            service.logs_metrics.forEach(log => {
                if (!dates[log.date]) {
                    dates.push(log.date)
                }
            })
        }
    })

    console.log(dates)

    const ctx = document.getElementById("logsPerServiceChart");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [
                {
                    label: "Auth Service",
                    data: [120, 190, 300, 250, 220, 170, 200],
                    borderColor: "#00ff87",
                    backgroundColor: "rgba(0,255,135,0.15)",
                    tension: 0.35
                },
                {
                    label: "API Gateway",
                    data: [90, 140, 180, 160, 200, 210, 230],
                    borderColor: "#ffd166",
                    backgroundColor: "rgba(255,209,102,0.15)",
                    tension: 0.35
                },
                {
                    label: "Database",
                    data: [40, 60, 55, 80, 70, 65, 90],
                    borderColor: "#ff6b6b",
                    backgroundColor: "rgba(255,107,107,0.15)",
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#c8e6c9"
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#6fae70" },
                    grid: { color: "rgba(255,255,255,0.05)" }
                },
                y: {
                    ticks: { color: "#6fae70" },
                    grid: { color: "rgba(255,255,255,0.05)" }
                }
            }
        }
    });

}

main()