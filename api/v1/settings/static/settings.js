class Settings {



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

    async fetchSettings() {
        try {
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
        } catch (error) {
            return `error: ${error}`
        }
    }

    async deleteAccount() {
        try {
            const response = await fetch("/api/v1/settings/account", {
                method: "DELETE",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                }
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while deleting your account: ${response.status}, ${data.message}`
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

    async changePassword(bodyData) {
        try {
            const response = await fetch("/auth/update_password", {
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
                    message: `HTTP error while changing your password: ${response.status}, ${data.message}`
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
    const settingsClass = new Settings()
    const credentials = await settingsClass.fetchCredentials()

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

    const settings = await settingsClass.fetchSettings()


    if (settings.message instanceof Object) {
        if (settings.message.auth_provider !== "LogArbor") {
            document.getElementById("settings-container").innerHTML = `<div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>Account</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 400px;" class="terminal-body">

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

                <div style="height: 400px;" class="terminal-body">

                    <div class="setting-row">
                        <label>API Key</label>
                        <p>Copy this and use it as a forth parameter(access token) in the log function, <a href="/docs/quick-setup">Learn More</a></p>
                        <input id="access_token_field" readonly type="text" value="${settings.message.id}" disabled>
                        <button class="btn small copyAccToken">Copy</button>
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

                    <button id="delete-account-button" style="margin-bottom: 20px;" class="btn danger">Delete Account</button>
                </div>
            </div>`
        } else {
            document.getElementById("settings-container").innerHTML = `<div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>Account</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 400px;" class="terminal-body">

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

                <div style="height: 400px;" class="terminal-body">

                    <div style="margin-bottom: 20px;" class="setting-row">
                        <label>Password</label>
                        <input id="change_password_new_input" type="password" placeholder="New password">
                        <button class="btn small change_password_button">Change</button>
                    </div>

                </div>
            </div>


            <!-- API -->
            <div style="margin-bottom: 50px;" class="terminal">
                <div class="terminal-header">
                    <span>API Keys</span>
                    <span class="terminal-dot"></span>
                </div>

                <div style="height: 400px;" class="terminal-body">

                    <div class="setting-row">
                        <label>Primary API Key</label>
                        <p>Copy this and use it as a forth parameter(access token) in the log function, <a href="/docs/quick-setup">Learn More</a></p>
                        <input id="access_token_field" readonly type="text" value="${settings.message.id}" disabled>
                        <button class="btn small copyAccToken">Copy</button>
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

                    <button style="margin-bottom: 20px;" class="btn danger delete-account-button">Delete Account</button>
                </div>
            </div>`
        }
    } else if (settings.message.includes("something went wrong")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("oauth user was not found")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("missing or invalid token")) {
        window.location.href = "/auth/login"
    } else if (settings.message.includes("user not found")) {
        window.location.href = "/auth/login"
    }

    const wrapper = document.getElementById("settings-wrapper")

    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('delete-account-button')) {


            const settingsClass = new Settings()
            const deleteAccountResult = await settingsClass.deleteAccount()

            if (deleteAccountResult.message.includes("user not found")) {
                alert("User was not found. Couldn't delete an account. Please contact support team for support.")
            } else if (deleteAccountResult.message.includes("something went wrong")) {
                alert("Something went wrong.")
            } else if (deleteAccountResult.message.includes("oauth user was not found")) {
                window.location.href = "/auth/login"
            } else if (deleteAccountResult.message.includes("missing or invalid token")) {
                window.location.href = "/auth/login"
            } else if (deleteAccountResult.message.includes("something went wrong while sending an email")) {
                alert("Something went wrong while sending an approval email. Please try again later.")
            } else if (deleteAccountResult.message.includes("aproval email sent")) {
                alert("An approval email was sent to your email. Please confirm.")
            }
        }

    })



    wrapper.addEventListener('click', (event) => {

        if (event.target.classList.contains('copyAccToken')) {

            const idValue = document.getElementById("access_token_field")

            idValue.select()
            idValue.setSelectionRange(0, 99999)

            navigator.clipboard.writeText(idValue.value)

        }

    })

    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('change_password_button')) {

            if (document.getElementById("change_password_new_input").value === "" || document.getElementById("change_password_new_input").value.length < 6 || document.getElementById("change_password_new_input").value.length > 15) {
                alert("Don't leave the new password input blank. Min: 6 characters, Max: 15 characters.")
            } else {
                document.getElementById("codeModal").style.display = "flex"
            }
        }

    })

    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('change_password_button_final')) {

            if (document.getElementById("codeModalInput").value === "") {
                alert("Don't leave the previous password blank.")
            } else {
                console.log("final change password button clicked")
                const bodyData = {
                    current_password: document.getElementById("codeModalInput").value,
                    new_password: document.getElementById("change_password_new_input").value
                }
                const settingsClass = new Settings()
                const deleteAccountResult = await settingsClass.changePassword(bodyData)

                if (deleteAccountResult.message.includes("user not found")) {
                    alert("User was not found. Couldn't change password. Please contact support team for support.")
                } else if (deleteAccountResult.message.includes("something went wrong")) {
                    alert("Something went wrong.")
                } else if (deleteAccountResult.message.includes("oauth user was not found")) {
                    window.location.href = "/auth/login"
                } else if (deleteAccountResult.message.includes("missing or invalid token")) {
                    window.location.href = "/auth/login"
                } else if (deleteAccountResult.message.includes("invalid password")) {
                    alert("Invalid password")
                } else if (deleteAccountResult.message.includes("password updated")) {
                    alert("Your password has been updated")
                    window.location.reload()
                }
            }
        }

    })

    wrapper.addEventListener('click', async (event) => {

        if (event.target.classList.contains('cancel_change_password')) {
            document.getElementById("codeModal").style.display = "none"
        }

    })
}

main()