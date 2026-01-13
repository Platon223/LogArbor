class Settings {



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

    async fetchSettings() {
        try{
            const response = await fetch("/api/v1/settings/settings", {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while getting settings of your account: ${response.status}, ${data.message}`
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
    const settingsClass = new Settings()
    const credentials = await settingsClass.fetchCredentials()

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

    const settings = await settingsClass.fetchSettings()

    if (settings.message instanceof Object) {
        if (settings.message.auth_provider !== "LogArbor") {
            document.getElementById("settings-container").innerHTML = `<div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>Account</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 600px;" class="terminal-body">

                    <div style="margin-bottom: 20px;" class="setting-row">
                        <label>Email</label>
                        <input readonly type="email" value="${settings.message.email}">
                    </div>

                    <div class="setting-row">
                        <label>Username</label>
                        <input readonly type="text" value="${settings.message.username}">
                    </div>

                </div>
            </div>

            <!-- API -->
            <div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>API Keys</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 600px;" class="terminal-body">

                    <div class="setting-row">
                        <label>API Key</label>
                        <input type="text" value="sk_live_************" disabled>
                        <button class="btn small">Regenerate</button>
                    </div>

                </div>
            </div>

            <!-- Danger Zone -->
            <div style="margin-bottom: 20px;" class="terminal danger-zone">
                <div class="terminal-header">
                    <span>Danger Zone</span>
                </div>

                <div style="height: 600px;" class="terminal-body">
                    <p style="margin-bottom: 14px; color: #ffb3b3;">
                        Deleting your account is permanent and cannot be undone.
                    </p>

                    <button style="margin-bottom: 20px;" class="btn danger">Delete Account</button>
                </div>
            </div>`
        } else {
            document.getElementById("settings-container").innerHTML = `<div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>Account</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 600px;" class="terminal-body">

                    <div style="margin-bottom: 20px;" class="setting-row">
                        <label>Email</label>
                        <input type="email" value="${settings.message.email}">
                        <button class="btn small">Update</button>
                    </div>

                    <div class="setting-row">
                        <label>Username</label>
                        <input type="text" value="${settings.message.username}">
                        <button class="btn small">Update</button>
                    </div>

                </div>
            </div>

            <!-- Security -->
            <div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>Security</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 600px;" class="terminal-body">

                    <div style="margin-bottom: 20px;" class="setting-row">
                        <label>Password</label>
                        <input type="password" placeholder="New password">
                        <button class="btn small">Change</button>
                    </div>

                </div>
            </div>


            <!-- API -->
            <div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>API Keys</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 600px;" class="terminal-body">

                    <div class="setting-row">
                        <label>Primary API Key</label>
                        <input type="text" value="sk_live_************" disabled>
                        <button class="btn small">Regenerate</button>
                    </div>

                </div>
            </div>

            <!-- Danger Zone -->
            <div style="margin-bottom: 20px;" class="terminal danger-zone">
                <div class="terminal-header">
                    <span>Danger Zone</span>
                </div>

                <div style="height: 600px;" class="terminal-body">
                    <p style="margin-bottom: 14px; color: #ffb3b3;">
                        Deleting your account is permanent and cannot be undone.
                    </p>

                    <button style="margin-bottom: 20px;" class="btn danger">Delete Account</button>
                </div>
            </div>`
        }
    } else if(settings.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("user not found")) {
        window.location.href = "/auth/login" 
    }
}

main()