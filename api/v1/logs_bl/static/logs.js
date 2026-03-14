class Logs {



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
            return `error: ${error}`
        }
    }





    async fetchLogs() {
        try {
            const response = await fetch("/api/v1/logs/all_logs", {
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
        } catch (error) {
            return `error: ${error}`
        }
    }





    async fetchMoreLogs(bodyData) {
        try {
            const response = await fetch("/api/v1/logs/all_logs_extra", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bodyData)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while getting more logs of your services: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch (error) {
            return `error: ${error}`
        }
    }





    async searchLogs(bodyData) {
        try {
            const response = await fetch("/api/v1/logs/search_by_message", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bodyData)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while searching logs: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch (error) {
            return `error: ${error}`
        }
    }





    async searchLogsByLevel(bodyData) {
        try {
            const response = await fetch("/api/v1/logs/search_by_level", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bodyData)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while searching logs by level: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch (error) {
            return `error: ${error}`
        }
    }





    async searchMoreLogs(bodyData) {
        try {
            const response = await fetch("/api/v1/logs/search_by_message_extra", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bodyData)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while searching more logs: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch (error) {
            return `error: ${error}`
        }
    }






    async searchLogsByLevelExtra(bodyData) {
        try {
            const response = await fetch("/api/v1/logs/search_by_level_extra", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bodyData)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while searching more logs by level: ${response.status}, ${data.message}`
                }
            }

            const data = await response.json()

            return {
                message: data.message
            }
        } catch (error) {
            return `error: ${error}`
        }
    }
}

async function main() {
    const logsClass = new Logs()

    logsClass.fetchCredentials().then(credentials => {
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
    });



    logsClass.fetchLogs().then(logs => {
        if (Array.isArray(logs.message)) {
            let servicesLogsContent = ""


            logs.message.forEach(element => {
                servicesLogsContent += `<section id="${element.service_id}" style='margin-bottom: 20px;' class="terminal-logs-page">
                    <div class="terminal-header">
                        <span>${element.service_name}</span>
                        <span class="terminal-dot green"></span>
                    </div>

                    <div class="terminal-body">
                        ${element.logs.length === 0 ? `No Logs Yet` : element.logs.reverse().map(logElement => `
                            <div class="log-line ${logElement.level}">
                                <span class="time">${logElement.time}</span>
                                <span class="level">${logElement.level}</span>
                                <span class="message">${logElement.message}</span>
                            </div>
                        `).join('')}

                        ${element.logs.length === 50 ? `<button class="filter-btn active load-more-logs">Load more</button>` : ``}
                    </div>

                    <div class="terminal-toolbar">
                        <input
                            type="text"
                            class="log-search"
                            placeholder="Search logs..."
                        >

                        <div class="log-filters">
                            <button class="filter-btn active search-trigger" data-level="all">Search</button>
                            <button class="filter-btn info info-search-button" data-level="info">INFO</button>
                            <button class="filter-btn warn warn-search-button" data-level="warn">WARN</button>
                            <button class="filter-btn error error-search-button" data-level="error">ERROR</button>
                            <button class="filter-btn error critical-search-button" data-level="error">CRITICAL</button>
                        </div>

                        <button onclick="location.reload()" class="clear-btn">Clear</button>
                    </div>

                </section>`
            })

            document.getElementById("terminalServicesWrapper").innerHTML = servicesLogsContent
        } else if (logs.message.includes("something went wrong")) {
            window.location.href = "/auth/login"
        } else if (logs.message.includes("oauth user was not found")) {
            window.location.href = "/auth/login"
        } else if (logs.message.includes("missing or invalid token")) {
            window.location.href = "/auth/login"
        } else if (logs.message.includes("no services")) {
            document.getElementById("terminalServicesWrapper").innerHTML = "No Services Yet"
        }
    });






    const socket = io("https://logarbor.com")

    console.log(localStorage.getItem("user_id"))

    socket.on("new-log", (data) => {

        if (data.user_id === localStorage.getItem("user_id")) {

            console.log("new log")
            logsClass.fetchLogs().then(logs => {
                if (Array.isArray(logs.message)) {
                    let servicesLogsContent = ""


                    logs.message.forEach(element => {
                        servicesLogsContent += `<section id="${element.service_id}" style='margin-bottom: 20px;' class="terminal-logs-page">
                            <div class="terminal-header">
                                <span>${element.service_name}</span>
                                <span class="terminal-dot green"></span>
                            </div>

                            <div class="terminal-body">
                                ${element.logs.length === 0 ? `No Logs Yet` : element.logs.reverse().map(logElement => `
                                    <div class="log-line ${logElement.level}">
                                        <span class="time">${logElement.time}</span>
                                        <span class="level">${logElement.level}</span>
                                        <span class="message">${logElement.message}</span>
                                    </div>
                                `).join('')}

                                ${element.logs.length === 50 ? `<button class="filter-btn active load-more-logs">Load more</button>` : ``}
                            </div>

                            <div class="terminal-toolbar">
                                <input
                                    type="text"
                                    class="log-search"
                                    placeholder="Search logs..."
                                >

                                <div class="log-filters">
                                    <button class="filter-btn active search-trigger" data-level="all">Search</button>
                                    <button class="filter-btn info info-search-button" data-level="info">INFO</button>
                                    <button class="filter-btn warn warn-search-button" data-level="warn">WARN</button>
                                    <button class="filter-btn error error-search-button" data-level="error">ERROR</button>
                                    <button class="filter-btn error critical-search-button" data-level="error">CRITICAL</button>
                                </div>

                                <button onclick="location.reload()" class="clear-btn">Clear</button>
                            </div>

                        </section>`
                    })

                    document.getElementById("terminalServicesWrapper").innerHTML = servicesLogsContent
                } else if (logs.message.includes("something went wrong")) {
                    window.location.href = "/auth/login"
                } else if (logs.message.includes("oauth user was not found")) {
                    window.location.href = "/auth/login"
                } else if (logs.message.includes("missing or invalid token")) {
                    window.location.href = "/auth/login"
                } else if (logs.message.includes("no services")) {
                    document.getElementById("terminalServicesWrapper").innerHTML = "No Services Yet"
                }
            });
        }
    })




    const wrapper = document.getElementById('terminalServicesWrapper')

    let extra = 100



    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('load-more-logs')) {


            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const loadMoreButton = terminalSection.querySelector(".load-more-logs")
            loadMoreButton.remove()

            const bodyData = {
                service_id: sectionId,
                extra: extra
            }


            const results = await logsClass.fetchMoreLogs(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                if (results.message.length === extra) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-logs">Load more</button>`
                    extra += 50
                }
            }
        }
    })





    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('search-trigger')) {


            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id


            const messageInput = terminalSection.querySelector('.log-search').value
            if (!messageInput) {
                alert("Please provide the log message")
            }

            const bodyData = {
                service_id: sectionId,
                message: messageInput
            }


            const results = await logsClass.searchLogs(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                if (results.message.length === 50) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-message">Load more</button>`
                }
            }
        }
    })





    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('info-search-button')) {


            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const bodyData = {
                service_id: sectionId,
                level: "info"
            }


            const results = await logsClass.searchLogsByLevel(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                if (results.message.length === 50) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-info">Load more</button>`
                }
            }
        }
    })





    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('warn-search-button')) {


            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const bodyData = {
                service_id: sectionId,
                level: "warning"
            }


            const results = await logsClass.searchLogsByLevel(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                if (results.message.length === 50) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-warn">Load more</button>`
                }
            }
        }
    })





    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('error-search-button')) {


            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const bodyData = {
                service_id: sectionId,
                level: "error"
            }


            const results = await logsClass.searchLogsByLevel(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                if (results.message.length === 50) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-error">Load more</button>`
                }
            }
        }
    })





    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('critical-search-button')) {


            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const bodyData = {
                service_id: sectionId,
                level: "critical"
            }


            const results = await logsClass.searchLogsByLevel(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                if (results.message.length === 50) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-critical">Load more</button>`
                }
            }
        }
    })




    wrapper.addEventListener("click", async (event) => {
        if (event.target.classList.contains("load-more-search-message")) {

            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const loadMoreButton = terminalSection.querySelector(".load-more-search-message")
            loadMoreButton.remove()

            const messageInput = terminalSection.querySelector('.log-search').value
            if (!messageInput) {
                alert("Please provide the log message")
            }

            const bodyData = {
                service_id: sectionId,
                message: messageInput,
                extra: extra
            }


            const results = await logsClass.searchMoreLogs(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                console.log(results.message.length)

                if (results.message.length === extra) {
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-message">Load more</button>`
                    extra += 50
                }
            }
        }
    })





    wrapper.addEventListener("click", async (event) => {
        if (event.target.classList.contains("load-more-search-info")) {

            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const loadMoreButton = terminalSection.querySelector(".load-more-search-info")
            loadMoreButton.remove()

            const bodyData = {
                service_id: sectionId,
                level: "info",
                extra: extra
            }


            const results = await logsClass.searchLogsByLevelExtra(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                console.log(results.message.length)

                if (results.message.length === extra) {
                    console.log("another more log button")
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-message">Load more</button>`
                    extra += 50
                }
            }
        }
    })





    wrapper.addEventListener("click", async (event) => {
        if (event.target.classList.contains("load-more-search-warn")) {

            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const loadMoreButton = terminalSection.querySelector(".load-more-search-warn")
            loadMoreButton.remove()

            const bodyData = {
                service_id: sectionId,
                level: "warning",
                extra: extra
            }


            const results = await logsClass.searchLogsByLevelExtra(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                console.log(results.message.length)

                if (results.message.length === extra) {
                    console.log("another more log button")
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-message">Load more</button>`
                    extra += 50
                }
            }
        }
    })





    wrapper.addEventListener("click", async (event) => {
        if (event.target.classList.contains("load-more-search-error")) {

            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const loadMoreButton = terminalSection.querySelector(".load-more-search-error")
            loadMoreButton.remove()

            const bodyData = {
                service_id: sectionId,
                level: "error",
                extra: extra
            }


            const results = await logsClass.searchLogsByLevelExtra(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                console.log(results.message.length)

                if (results.message.length === extra) {
                    console.log("another more log button")
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-message">Load more</button>`
                    extra += 50
                }
            }
        }
    })





    wrapper.addEventListener("click", async (event) => {
        if (event.target.classList.contains("load-more-search-critical")) {

            const terminalSection = event.target.closest('section')
            const sectionId = terminalSection.id

            const loadMoreButton = terminalSection.querySelector(".load-more-search-critical")
            loadMoreButton.remove()

            const bodyData = {
                service_id: sectionId,
                level: "critical",
                extra: extra
            }


            const results = await logsClass.searchLogsByLevelExtra(bodyData)

            if (results.message.includes("service not found")) {
                alert("Service was not found. Please try again later or contact our support.")
            } else if (results.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (results.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (results.message.includes("no logs found")) {
                terminalSection.querySelector('.terminal-body').innerHTML = "No logs found"
            } else if (Array.isArray(results.message)) {
                const terminalBody = terminalSection.querySelector('.terminal-body')
                terminalBody.innerHTML = results.message.map(log => `
                    <div class="log-line ${log.level}">
                        <span class="time">${log.time}</span>
                        <span class="level">${log.level}</span>
                        <span class="message">${log.message}</span>
                    </div>
                `).join('')

                console.log(results.message.length)

                if (results.message.length === extra) {
                    console.log("another more log button")
                    terminalBody.innerHTML += `<button class="filter-btn active load-more-search-message">Load more</button>`
                    extra += 50
                }
            }
        }
    })
}

main()