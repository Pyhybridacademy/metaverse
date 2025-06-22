// Mobile menu toggle
document.addEventListener("DOMContentLoaded", () => {
  const mobileMenuBtn = document.getElementById("mobile-menu-btn")
  const sidebar = document.getElementById("sidebar")
  const sidebarOverlay = document.getElementById("sidebar-overlay")
  const userMenuBtn = document.getElementById("user-menu-btn")
  const userMenu = document.getElementById("user-menu")

  // Mobile sidebar toggle
  if (mobileMenuBtn && sidebar && sidebarOverlay) {
    mobileMenuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("-translate-x-full")
      sidebarOverlay.classList.toggle("hidden")
    })

    sidebarOverlay.addEventListener("click", () => {
      sidebar.classList.add("-translate-x-full")
      sidebarOverlay.classList.add("hidden")
    })
  }

  // User menu dropdown
  if (userMenuBtn && userMenu) {
    userMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation()
      userMenu.classList.toggle("hidden")
    })

    // Close dropdown when clicking outside
    document.addEventListener("click", () => {
      userMenu.classList.add("hidden")
    })

    userMenu.addEventListener("click", (e) => {
      e.stopPropagation()
    })
  }

  // Auto-hide messages after 5 seconds
  const messages = document.querySelectorAll(".alert")
  messages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      setTimeout(() => {
        message.remove()
      }, 300)
    }, 5000)
  })
})

// Form validation helpers
function validateForm(formId) {
  const form = document.getElementById(formId)
  if (!form) return true

  const requiredFields = form.querySelectorAll("[required]")
  let isValid = true

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      field.classList.add("border-red-500")
      isValid = false
    } else {
      field.classList.remove("border-red-500")
    }
  })

  return isValid
}

// Number formatting
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount)
}

// Copy to clipboard function
function copyToClipboard(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showNotification("Copied to clipboard!", "success")
    })
  } else {
    // Fallback for older browsers
    const textArea = document.createElement("textarea")
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand("copy")
    document.body.removeChild(textArea)
    showNotification("Copied to clipboard!", "success")
  }
}

// Show notification
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `fixed top-4 right-4 z-50 p-4 rounded shadow-lg max-w-sm ${
    type === "success"
      ? "bg-green-500 text-white"
      : type === "error"
        ? "bg-red-500 text-white"
        : type === "warning"
          ? "bg-yellow-500 text-white"
          : "bg-blue-500 text-white"
  }`
  notification.innerHTML = `
        <div class="flex justify-between items-center">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `

  document.body.appendChild(notification)

  setTimeout(() => {
    notification.remove()
  }, 5000)
}
