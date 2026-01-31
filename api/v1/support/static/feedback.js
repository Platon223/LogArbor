class Feedback {



    async sendFeedback(feedbackData) {

        try{
            const response = await fetch("/api/v1/support/feedback", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(feedbackData)
            })

            if (!response.ok) {
                const data = await response.json()
                return {
                    message: `HTTP error while submiting feedback: ${response.status}, ${data.message}`
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

const feedbackForm = document.querySelector(".support-form")

feedbackForm.addEventListener("submit", async (event) => {
    event.preventDefault()

    const emailValue = document.getElementById("email").value
    const subjectValue = document.getElementById("subject").value
    const messageValue = document.getElementById("message").value

    const feedbackData = {
        email: emailValue,
        subject: subjectValue,
        message: messageValue
    }

    const feedbackClass = new Feedback()

    const feedbackResult = await feedbackClass.sendFeedback(feedbackData)

    if (feedbackResult.message.includes("invalid email")) {
        alert("Provide a valid email please.")
    } else if(feedbackResult.message.includes("something went wrong")) {
        alert("Something went wrong while sending an email. Please try again later.")
    } else if (feedbackResult.message.includes("sent a feedback email")) {
        alert("Your feedback was sent. Please check your inbox for response from LogArbor Support Team soon.")
    }
})