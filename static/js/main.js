// Main JS file for Bob the Whisky Expert

document.addEventListener("DOMContentLoaded", function () {
  // Ensure loading spinner is hidden on page load
  const loadingSpinner = document.getElementById("loading-spinner");
  if (loadingSpinner) {
    loadingSpinner.style.display = "none";
  }

  // Form validation
  const usernameForm = document.getElementById("username-form");
  if (usernameForm) {
    usernameForm.addEventListener("submit", function (event) {
      const usernameInput = document.getElementById("username");
      if (!usernameInput.value.trim()) {
        event.preventDefault();
        alert("Please enter a BAXUS username");
        return;
      }

      // Show loading spinner only when submitting the form
      if (loadingSpinner) {
        loadingSpinner.style.display = "block";
      }

      // Hide the form
      usernameForm.style.display = "none";
    });
  }

  // Bootstrap tooltips initialization
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Flavor profile visualization
  const flavorContainers = document.querySelectorAll(
    ".flavor-profile-container"
  );
  flavorContainers.forEach((container) => {
    const flavorData = JSON.parse(container.dataset.flavors || "{}");

    // Clear any existing content
    container.innerHTML = "";

    // Create tag-based flavor profile visualization
    for (const [flavor, value] of Object.entries(flavorData)) {
      if (value > 0) {
        // Skip values that are too low to be meaningful
        if (value < 10) continue;

        const flavorTag = document.createElement("span");
        flavorTag.className = "flavor-tag";

        // Determine level based on value
        let level = "low";
        if (value > 70) {
          level = "high";
        } else if (value > 35) {
          level = "medium";
        }

        flavorTag.setAttribute("data-level", level);
        flavorTag.textContent =
          flavor.charAt(0).toUpperCase() + flavor.slice(1);
        container.appendChild(flavorTag);
      }
    }

    // If there are no flavor tags, add a message
    if (container.children.length === 0) {
      const noFlavorMsg = document.createElement("p");
      noFlavorMsg.className = "text-muted small mb-0";
      noFlavorMsg.textContent = "No flavor profile data available";
      container.appendChild(noFlavorMsg);
    }
  });

  // Theme switching functionality
  const themeToggle = document.getElementById("themeToggle");
  const lightIcon = document.getElementById("lightIcon");
  const darkIcon = document.getElementById("darkIcon");
  const html = document.documentElement;

  // Check for saved theme preference, otherwise use system preference
  const savedTheme = localStorage.getItem("theme");
  const systemPrefersDark = window.matchMedia(
    "(prefers-color-scheme: dark)"
  ).matches;

  // Set initial theme
  if (savedTheme) {
    html.setAttribute("data-bs-theme", savedTheme);
    updateIcons(savedTheme === "dark");
  } else {
    html.setAttribute("data-bs-theme", systemPrefersDark ? "dark" : "light");
    updateIcons(systemPrefersDark);
  }

  // Toggle theme on button click
  themeToggle.addEventListener("click", function () {
    const isDark = html.getAttribute("data-bs-theme") === "dark";
    const newTheme = isDark ? "light" : "dark";

    html.setAttribute("data-bs-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateIcons(!isDark);
  });

  // Function to update icon visibility
  function updateIcons(isDark) {
    lightIcon.style.display = isDark ? "none" : "inline-block";
    darkIcon.style.display = isDark ? "inline-block" : "none";
  }
});
