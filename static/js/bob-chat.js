// Bob Chat Widget JavaScript
document.addEventListener("DOMContentLoaded", function () {
  // Chat widget elements
  const chatWidget = document.getElementById("bobChatWidget");
  const chatHeader = document.getElementById("bobChatHeader");
  const chatBody = document.getElementById("bobChatBody");
  const chatToggle = document.getElementById("bobChatToggle");
  const chatForm = document.getElementById("bobChatForm");
  const chatInput = document.getElementById("bobChatInput");
  const chatMessages = document.getElementById("bobMessages");
  const resetButton = document.getElementById("resetBobChat");
  const suggestionLinks = document.querySelectorAll(".suggestion-link");

  console.log("Chat elements loaded", {
    chatWidget: !!chatWidget,
    chatHeader: !!chatHeader,
    chatBody: !!chatBody,
    chatToggle: !!chatToggle,
    chatForm: !!chatForm,
    chatInput: !!chatInput,
    chatMessages: !!chatMessages,
    resetButton: !!resetButton,
  });

  // Toggle chat widget
  function toggleChatWidget() {
    console.log("Toggling chat widget");
    const isCollapsed = chatBody.classList.contains("collapsed");

    if (isCollapsed) {
      chatBody.classList.remove("collapsed");
      chatToggle.querySelector("i").className = "fas fa-minus";
      setTimeout(() => chatInput.focus(), 300);
    } else {
      chatBody.classList.add("collapsed");
      chatToggle.querySelector("i").className = "fas fa-plus";
    }
  }

  // Click handlers for chat toggle
  chatToggle.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    toggleChatWidget();
  });

  // Handle form submission
  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (message) {
      sendMessage(message);
      chatInput.value = "";
    }
  });

  // Send a message
  function sendMessage(message) {
    console.log("Sending message:", message);

    // Show user message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "message user-message";
    userMessageDiv.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(userMessageDiv);

    // Show typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "message bot-message typing-indicator";
    typingIndicator.id = "typingIndicator";
    typingIndicator.innerHTML = "<span></span><span></span><span></span>";
    chatMessages.appendChild(typingIndicator);

    // Scroll down
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Call API
    fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => {
        console.log("Response status:", response.status);
        return response.json();
      })
      .then((data) => {
        console.log("Response data:", data);

        // Remove typing indicator
        const indicator = document.getElementById("typingIndicator");
        if (indicator) {
          chatMessages.removeChild(indicator);
        }

        // Add bot response
        const botMessageDiv = document.createElement("div");
        botMessageDiv.className = "message bot-message";

        // Format the message with markdown-like syntax
        let formattedContent = data.response
          .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
          .replace(/\*(.*?)\*/g, "<em>$1</em>")
          .replace(/\n\n/g, "</p><p>")
          .replace(/\n/g, "<br>");

        botMessageDiv.innerHTML = `<p>${formattedContent}</p>`;
        chatMessages.appendChild(botMessageDiv);

        // Scroll down
        chatMessages.scrollTop = chatMessages.scrollHeight;
      })
      .catch((error) => {
        console.error("Error sending message:", error);

        // Remove typing indicator
        const indicator = document.getElementById("typingIndicator");
        if (indicator) {
          chatMessages.removeChild(indicator);
        }

        // Show error message
        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.className = "message bot-message error";
        errorMessageDiv.innerHTML =
          "<p>Sorry, I encountered a problem. Please try again.</p>";
        chatMessages.appendChild(errorMessageDiv);

        // Scroll down
        chatMessages.scrollTop = chatMessages.scrollHeight;
      });
  }

  // Handle suggestion links
  suggestionLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const suggestion = this.textContent.trim();
      chatInput.value = suggestion;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  // Reset chat
  if (resetButton) {
    resetButton.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      console.log("Resetting chat");

      // Clear messages except welcome message
      while (chatMessages.children.length > 1) {
        chatMessages.removeChild(chatMessages.lastChild);
      }

      // Reset server-side chat history
      fetch("/chat/reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Reset response:", data);
          if (data.success) {
            // Show reset confirmation
            const resetMsg = document.createElement("div");
            resetMsg.className = "system-message";
            resetMsg.textContent = "Chat history has been reset";
            chatMessages.appendChild(resetMsg);

            // Remove after 2 seconds
            setTimeout(() => {
              chatMessages.removeChild(resetMsg);
            }, 2000);
          }
        })
        .catch((error) => {
          console.error("Error resetting chat:", error);
        });
    });
  }

  console.log("Chat widget initialized");
});
