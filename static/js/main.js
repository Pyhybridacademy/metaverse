function getCSRFToken() {
  let token = window.CSRF_TOKEN || ""
  if (!token) {
    // Fallback: Get token from cookie
    const name = "csrftoken"
    const cookies = document.cookie.split(";")
    for (let cookie of cookies) {
      cookie = cookie.trim()
      if (cookie.startsWith(name + "=")) {
        token = cookie.substring(name.length + 1)
        break
      }
    }
  }
  console.log("CSRF Token:", token, "Length:", token.length)
  return token
}

function showLoading(button) {
  const originalText = button.innerHTML
  button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...'
  button.disabled = true
  return originalText
}

function hideLoading(button, originalText) {
  button.innerHTML = originalText
  button.disabled = false
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount)
}

function copyToClipboard(text) {
  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        showNotification("Copied to clipboard!", "success")
      })
      .catch((err) => {
        console.error("Clipboard error:", err)
        showNotification("Failed to copy to clipboard.", "error")
      })
  } else {
    const textArea = document.createElement("textarea")
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand("copy")
    document.body.removeChild(textArea)
    showNotification("Copied to clipboard!", "success")
  }
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  const classes = {
    success: "bg-green-100 border-green-500 text-green-700",
    error: "bg-red-100 border-red-500 text-red-700",
    warning: "bg-yellow-100 border-yellow-500 text-yellow-700",
    info: "bg-blue-100 border-blue-500 text-blue-700",
  }
  notification.className = `fixed top-4 right-4 z-50 p-4 rounded shadow-lg max-w-sm border-l-4 ${classes[type] || classes.info} transition-all duration-300 transform translate-x-full`
  notification.innerHTML = `
        <div class="flex justify-between items-center">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `
  document.body.appendChild(notification)
  setTimeout(() => notification.classList.remove("translate-x-full"), 100)
  setTimeout(() => {
    notification.classList.add("translate-x-full")
    setTimeout(() => notification.remove(), 300)
  }, 5000)
}

// Sidebar and Menu Toggle
document.addEventListener("DOMContentLoaded", () => {
  const mobileMenuBtn = document.getElementById("admin-mobile-menu-btn")
  const sidebar = document.getElementById("admin-sidebar")
  const sidebarOverlay = document.getElementById("admin-sidebar-overlay")
  const userMenuBtn = document.getElementById("admin-user-menu-btn")
  const userMenu = document.getElementById("admin-user-menu")

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

  if (userMenuBtn && userMenu) {
    userMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation()
      userMenu.classList.toggle("hidden")
    })

    document.addEventListener("click", (e) => {
      if (!userMenu.contains(e.target) && !userMenuBtn.contains(e.target)) {
        userMenu.classList.add("hidden")
      }
    })
  }

  // Auto-hide messages
  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0"
      setTimeout(() => alert.remove(), 300)
    }, 5000)
  })
})

// Modal Functions
function openAddInvestmentModal() {
  const modal = document.getElementById("addInvestmentModal")
  if (modal) {
    modal.classList.remove("hidden")
    document.body.style.overflow = "hidden"
  } else {
    console.error("Add Investment Modal not found")
    showNotification("Error: Modal not found.", "error")
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId)
  if (modal) {
    modal.classList.add("hidden")
    document.body.style.overflow = "auto"
  } else {
    console.error(`Modal with ID ${modalId} not found`)
  }
}

function toggleFilters() {
  const filtersSection = document.getElementById("filtersSection")
  if (filtersSection) {
    filtersSection.classList.toggle("hidden")
  } else {
    console.error("Filters section not found")
  }
}

function updateAmountLimits(selectElement) {
  const selectedOption = selectElement.options[selectElement.selectedIndex]
  const minAmount = selectedOption.getAttribute("data-min")
  const maxAmount = selectedOption.getAttribute("data-max")
  const amountInput = document.querySelector('input[name="amount"]')
  const limitsText = document.getElementById("amountLimits")

  if (minAmount && maxAmount && amountInput && limitsText) {
    amountInput.setAttribute("min", minAmount)
    amountInput.setAttribute("max", maxAmount)
    limitsText.textContent = `Amount must be between $${minAmount} and $${maxAmount}`
    limitsText.className = "text-sm text-blue-600 mt-1"
  } else {
    if (limitsText) {
      limitsText.textContent = "Select a plan to see amount limits"
      limitsText.className = "text-sm text-gray-500 mt-1"
    }
  }
}

// Investment Actions
function viewInvestmentDetail(investmentId) {
  const modal = document.getElementById("investmentDetailModal")
  const content = document.getElementById("investmentDetailContent")

  if (!modal || !content) {
    console.error("Investment detail modal or content not found")
    showNotification("Error: Modal not found.", "error")
    return
  }

  content.innerHTML =
    '<div class="flex justify-center items-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>'
  modal.classList.remove("hidden")
  document.body.style.overflow = "hidden"

  fetch(`/admin-panel/investments/${investmentId}/detail/`, {
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      return response.text()
    })
    .then((html) => {
      content.innerHTML = html
    })
    .catch((error) => {
      console.error("Error fetching investment details:", error)
      content.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-3xl text-red-400 mb-4"></i>
                    <p class="text-red-600">Error loading investment details</p>
                    <button onclick="closeModal('investmentDetailModal')" class="mt-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600">Close</button>
                </div>
            `
      showNotification("Failed to load investment details.", "error")
    })
}

function editInvestment(investmentId) {
  const modal = document.getElementById("editInvestmentModal")
  const content = document.getElementById("editInvestmentContent")

  if (!modal || !content) {
    console.error("Edit investment modal or content not found")
    showNotification("Error: Modal not found.", "error")
    return
  }

  content.innerHTML =
    '<div class="flex justify-center items-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>'
  modal.classList.remove("hidden")
  document.body.style.overflow = "hidden"

  fetch(`/admin-panel/investments/${investmentId}/edit-form/`, {
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      return response.text()
    })
    .then((html) => {
      content.innerHTML = html
      // Attach form submission handler
      const form = content.querySelector("form")
      if (form) {
        form.addEventListener("submit", handleEditInvestmentSubmit)
      }
    })
    .catch((error) => {
      console.error("Error fetching edit form:", error)
      content.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-3xl text-red-400 mb-4"></i>
                    <p class="text-red-600">Error loading edit form</p>
                    <button onclick="closeModal('editInvestmentModal')" class="mt-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600">Close</button>
                </div>
            `
      showNotification("Failed to load edit form.", "error")
    })
}

function handleEditInvestmentSubmit(e) {
  e.preventDefault()
  const form = e.target
  const submitButton = form.querySelector('button[type="submit"]')
  const originalText = showLoading(submitButton)

  const formData = new FormData(form)
  fetch(form.action, {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      return response.json()
    })
    .then((data) => {
      hideLoading(submitButton, originalText)
      if (data.success) {
        closeModal("editInvestmentModal")
        showNotification("Investment updated successfully!", "success")
        setTimeout(() => location.reload(), 1000)
      } else {
        showNotification(`Error: ${data.error || "Unknown error occurred"}`, "error")
      }
    })
    .catch((error) => {
      hideLoading(submitButton, originalText)
      console.error("Error updating investment:", error)
      showNotification("Error updating investment. Please try again.", "error")
    })
}

function completeInvestment(investmentId) {
  if (
    !confirm(
      "Are you sure you want to mark this investment as completed? This will add the returns to the user's account.",
    )
  ) {
    return
  }

  const button = event.target.closest("button")
  const originalText = showLoading(button)
  const csrfToken = getCSRFToken()

  if (!csrfToken || csrfToken.length !== 64) {
    console.error("Invalid CSRF token:", csrfToken)
    showNotification("Error: Invalid CSRF token. Please refresh the page.", "error")
    hideLoading(button, originalText)
    return
  }

  fetch(`/admin-panel/investments/${investmentId}/complete/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((err) => {
          throw new Error(err.error || `HTTP error! status: ${response.status}`)
        })
      }
      return response.json()
    })
    .then((data) => {
      hideLoading(button, originalText)
      if (data.success) {
        showNotification("Investment completed successfully!", "success")
        setTimeout(() => location.reload(), 1000)
      } else {
        showNotification(`Error: ${data.error || "Unknown error occurred"}`, "error")
      }
    })
    .catch((error) => {
      hideLoading(button, originalText)
      console.error("Error completing investment:", error)
      showNotification(`Error completing investment: ${error.message}`, "error")
    })
}

function cancelInvestment(investmentId) {
  if (!confirm("Are you sure you want to cancel this investment? This will refund the amount to the user's account.")) {
    return
  }

  const button = event.target.closest("button")
  const originalText = showLoading(button)
  const csrfToken = getCSRFToken()

  if (!csrfToken || csrfToken.length !== 64) {
    console.error("Invalid CSRF token:", csrfToken)
    showNotification("Error: Invalid CSRF token. Please refresh the page.", "error")
    hideLoading(button, originalText)
    return
  }

  fetch(`/admin-panel/investments/${investmentId}/cancel/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((err) => {
          throw new Error(err.error || `HTTP error! status: ${response.status}`)
        })
      }
      return response.json()
    })
    .then((data) => {
      hideLoading(button, originalText)
      if (data.success) {
        showNotification("Investment cancelled successfully!", "success")
        setTimeout(() => location.reload(), 1000)
      } else {
        showNotification(`Error: ${data.error || "Unknown error occurred"}`, "error")
      }
    })
    .catch((error) => {
      hideLoading(button, originalText)
      console.error("Error cancelling investment:", error)
      showNotification(`Error cancelling investment: ${error.message}`, "error")
    })
}

// Form Validation
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

// Modal Close on Outside Click and Escape Key
document.addEventListener("click", (event) => {
  const modals = ["addInvestmentModal", "investmentDetailModal", "editInvestmentModal"]
  modals.forEach((modalId) => {
    const modal = document.getElementById(modalId)
    if (modal && event.target === modal) {
      modal.classList.add("hidden")
      document.body.style.overflow = "auto"
    }
  })
})

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const modals = ["addInvestmentModal", "investmentDetailModal", "editInvestmentModal"]
    modals.forEach((modalId) => {
      const modal = document.getElementById(modalId)
      if (modal && !modal.classList.contains("hidden")) {
        modal.classList.add("hidden")
        document.body.style.overflow = "auto"
      }
    })
  }
})

// Add Investment Form Submission
document.addEventListener("DOMContentLoaded", () => {
  const addInvestmentForm = document.querySelector("#addInvestmentModal form")
  if (addInvestmentForm) {
    addInvestmentForm.addEventListener("submit", function (e) {
      e.preventDefault()
      if (!validateForm("addInvestmentModal")) {
        showNotification("Please fill all required fields.", "error")
        return
      }

      const submitButton = this.querySelector('button[type="submit"]')
      const originalText = showLoading(submitButton)

      const formData = new FormData(this)
      fetch(this.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
      })
        .then((response) => {
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
          return response.json()
        })
        .then((data) => {
          hideLoading(submitButton, originalText)
          if (data.success) {
            closeModal("addInvestmentModal")
            showNotification("Investment added successfully!", "success")
            setTimeout(() => location.reload(), 1000)
          } else {
            showNotification(`Error: ${data.error || "Unknown error occurred"}`, "error")
          }
        })
        .catch((error) => {
          hideLoading(submitButton, originalText)
          console.error("Error adding investment:", error)
          showNotification("Error adding investment. Please try again.", "error")
        })
    })
  }
})
