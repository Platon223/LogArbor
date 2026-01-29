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

    const services_data = []

    metrics.message.forEach(service => {
        if (service.logs_metrics.length !== 1) {
            service.logs_metrics.forEach(log => {
                if (!dates.includes(log.date) && log.date !== "") {
                    dates.push(log.date)
                }
            })
        }
    })

    const randomBackgroundColors = ["rgba(0,255,135,0.80)", "rgba(255,209,102,0.80)", "rgba(255,107,107,0.80)", "rgba(255, 0, 189, 0.80)", "rgba(157, 0, 255, 0.80)", "rgba(135, 206, 235, 0.80)", "rgba(168, 220, 171, 0.80)"]

    metrics.message.forEach(service => {
        const service_dataset = {}

        service_dataset.label = service.service_name

        const log_count_array = []

        service.logs_metrics.forEach(log => {
            if (log.date !== "") {
                log_count_array.push(log.count)
            }
        })

        const randomColor = randomBackgroundColors[Math.floor(Math.random() * randomBackgroundColors.length)]

        service_dataset.data = log_count_array
        service_dataset.borderColor = randomColor
        service_dataset.backgroundColor = randomColor
        service_dataset.tension = 0.35

        let indexRandomColor = randomBackgroundColors.indexOf(randomColor)

        if (indexRandomColor > -1) {
            randomBackgroundColors.splice(indexRandomColor, 1)
        }

        services_data.push(service_dataset)

    })

    console.log(dates)

    const ctx = document.getElementById("logsPerServiceChart");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: services_data
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