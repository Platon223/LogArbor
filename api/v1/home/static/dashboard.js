class Dashboard {



    async fetchCredentials() {

        try {
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
        } catch (error) {
            return { message: `error: ${error}` }
        }
    }

    async fetchMetrics() {

        try {
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
        } catch (error) {
            return { message: `error: ${error}` }
        }
    }

    async fetchSpeedMetrics() {

        try {
            const response = await fetch("/api/v1/logs/logs_speed_metric", {
                method: "POST",
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
        } catch (error) {
            return { message: `error: ${error}` }
        }
    }

}

async function main() {
    const dashboardClass = new Dashboard()
    const credentials = await dashboardClass.fetchCredentials()

    console.log(credentials.message)

    if (credentials.message.includes("user not found")) {
        window.location.href = "/auth/register"
    } else if (credentials.message.includes("something went wrong")) {
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

    let smallestDate = 999999999999

    metrics.message.forEach(service => {
        if (service.logs_metrics.length !== 1) {
            service.logs_metrics.forEach(log => {
                let logDate = log.date
                if (!dates.includes(Number(logDate.replace(/-/g, ""))) && log.date !== "") {
                    let dateAsNumber = Number(logDate.replace(/-/g, ""))
                    dates.push(dateAsNumber)
                }
            })
        }
    })

    dates.sort((a, b) => a - b)

    dates.forEach((date, index) => {
        const dateAsString = date.toString()
        const formatedString = dateAsString.slice(0, 4) + "-" + dateAsString.slice(4, 6) + "-" + dateAsString.slice(6)

        dates[index] = formatedString
    })

    const randomBackgroundColors = ["rgba(0,255,135,0.7)", "rgba(255,209,102,0.7)", "rgba(255,107,107,0.7)", "rgba(5, 60, 225, 0.7)", "rgba(255, 0, 0, 0.7)", "rgba(135, 206, 235, 0.7)", "rgba(168, 220, 171, 0.7)"]

    metrics.message.forEach(service => {
        const service_dataset = {}

        service_dataset.label = service.service_name

        const log_count_array = []

        service.logs_metrics.forEach(log => {
            if (log.date !== "") {
                const indexInLogCountArray = dates.indexOf(log.date)

                log_count_array[indexInLogCountArray] = log.count
            }
        })

        if (localStorage.getItem(`${service.service_id}`)) {
            service_dataset.borderColor = localStorage.getItem(`${service.service_id}`)
            service_dataset.backgroundColor = localStorage.getItem(`${service.service_id}`)
            service_dataset.tension = 0.35
            service_dataset.data = log_count_array

            let indexRandomColor = randomBackgroundColors.indexOf(localStorage.getItem(`${service.service_id}`))

            if (indexRandomColor > -1) {
                randomBackgroundColors.splice(indexRandomColor, 1)
            }

            services_data.push(service_dataset)

        } else {

            const randomColor = randomBackgroundColors[Math.floor(Math.random() * randomBackgroundColors.length)]

            service_dataset.data = log_count_array
            service_dataset.borderColor = randomColor
            service_dataset.backgroundColor = randomColor
            service_dataset.tension = 0.35

            let indexRandomColor = randomBackgroundColors.indexOf(randomColor)

            if (indexRandomColor > -1) {
                randomBackgroundColors.splice(indexRandomColor, 1)
            }

            localStorage.setItem(`${service.service_id}`, randomColor)

            services_data.push(service_dataset)


        }

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
            animation: true,
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

    const speedMetrics = await dashboardClass.fetchSpeedMetrics()

    speedData = []

    speedAllServices = []

    speedMetrics.message.forEach(metric => {
        speedAllServices.push({ label: metric.service_name, borderColor: localStorage.getItem(metric.service_id), backgroundColor: localStorage.getItem(metric.service_id) })
    })

    speedMetrics.message.forEach(metric => {
        speedData.push(metric.speed)
    })

    const ctxSpeedMetric = document.getElementById('logSpeedChart')

    new Chart(ctxSpeedMetric, {
        type: "bar",
        data: {
            labels: speedData,
            datasets: speedAllServices
        },
        options: {
            animation: true,
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
    })

    console.log(speedMetrics)

    const socket = io({
        transports: ["websocket"],
        auth: {
            user_id: localStorage.getItem("user_id")
        }
    })

    socket.on("new-log", async (data) => {
        const metrics = await dashboardClass.fetchMetrics()

        console.log(metrics)

        const dates = []

        const services_data = []

        let smallestDate = 999999999999

        metrics.message.forEach(service => {
            if (service.logs_metrics.length !== 1) {
                service.logs_metrics.forEach(log => {
                    let logDate = log.date
                    if (!dates.includes(Number(logDate.replace(/-/g, ""))) && log.date !== "") {
                        let dateAsNumber = Number(logDate.replace(/-/g, ""))
                        dates.push(dateAsNumber)
                    }
                })
            }
        })

        dates.sort((a, b) => a - b)

        dates.forEach((date, index) => {
            const dateAsString = date.toString()
            const formatedString = dateAsString.slice(0, 4) + "-" + dateAsString.slice(4, 6) + "-" + dateAsString.slice(6)

            dates[index] = formatedString
        })

        const randomBackgroundColors = ["rgba(0,255,135,0.7)", "rgba(255,209,102,0.7)", "rgba(255,107,107,0.7)", "rgba(5, 60, 225, 0.7)", "rgba(255, 0, 0, 0.7)", "rgba(135, 206, 235, 0.7)", "rgba(168, 220, 171, 0.7)"]

        metrics.message.forEach(service => {
            const service_dataset = {}

            service_dataset.label = service.service_name

            const log_count_array = []

            service.logs_metrics.forEach(log => {
                if (log.date !== "") {
                    const indexInLogCountArray = dates.indexOf(log.date)

                    log_count_array[indexInLogCountArray] = log.count
                }
            })

            if (localStorage.getItem(`${service.service_id}`)) {
                service_dataset.borderColor = localStorage.getItem(`${service.service_id}`)
                service_dataset.backgroundColor = localStorage.getItem(`${service.service_id}`)
                service_dataset.tension = 0.35
                service_dataset.data = log_count_array

                let indexRandomColor = randomBackgroundColors.indexOf(localStorage.getItem(`${service.service_id}`))

                if (indexRandomColor > -1) {
                    randomBackgroundColors.splice(indexRandomColor, 1)
                }

                services_data.push(service_dataset)

            } else {

                const randomColor = randomBackgroundColors[Math.floor(Math.random() * randomBackgroundColors.length)]

                service_dataset.data = log_count_array
                service_dataset.borderColor = randomColor
                service_dataset.backgroundColor = randomColor
                service_dataset.tension = 0.35

                let indexRandomColor = randomBackgroundColors.indexOf(randomColor)

                if (indexRandomColor > -1) {
                    randomBackgroundColors.splice(indexRandomColor, 1)
                }

                localStorage.setItem(`${service.service_id}`, randomColor)

                services_data.push(service_dataset)


            }



        })

        console.log(dates)

        const chartInstance = Chart.getChart("logsPerServiceChart")

        chartInstance.destroy()

        const ctx = document.getElementById("logsPerServiceChart");

        new Chart(ctx, {
            type: "line",
            data: {
                labels: dates,
                datasets: services_data
            },
            options: {
                animation: false,
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

    })


}

main()