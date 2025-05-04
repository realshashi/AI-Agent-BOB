// Main JS file for Bob the Whisky Expert

document.addEventListener("DOMContentLoaded", function () {
  // Initialize tooltips
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach((tooltip) => {
    new bootstrap.Tooltip(tooltip);
  });

  // Handle username form submission
  const usernameForm = document.getElementById("username-form");
  const loadingSpinner = document.getElementById("loading-spinner");

  if (usernameForm) {
    usernameForm.addEventListener("submit", function (event) {
      const usernameInput = document.getElementById("username");
      if (!usernameInput.value.trim()) {
        event.preventDefault();
        alert("Please enter a BAXUS username");
        return;
      }

      usernameForm.style.display = "none";
      loadingSpinner.style.display = "block";
    });
  }

  // Flavor profile visualization
  const flavorContainers = document.querySelectorAll(
    ".flavor-profile-container"
  );
  flavorContainers.forEach((container) => {
    const flavorData = JSON.parse(container.dataset.flavors || "{}");

    // Clear any existing content
    container.innerHTML = "";

    // Sort flavors by value to show strongest first
    const sortedFlavors = Object.entries(flavorData)
      .sort(([, a], [, b]) => b - a)
      .filter(([, value]) => value >= 10); // Only show flavors with value >= 10

    if (sortedFlavors.length > 0) {
      sortedFlavors.forEach(([flavor, value]) => {
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
        // Capitalize first letter and format flavor name
        const formattedFlavor =
          flavor.charAt(0).toUpperCase() + flavor.slice(1).replace(/_/g, " ");
        flavorTag.textContent = formattedFlavor;

        // Add tooltip with percentage
        flavorTag.setAttribute("data-bs-toggle", "tooltip");
        flavorTag.setAttribute("title", `${Math.round(value)}%`);

        container.appendChild(flavorTag);
        new bootstrap.Tooltip(flavorTag);
      });
    } else {
      // If no significant flavors, show a message
      const noFlavorMsg = document.createElement("p");
      noFlavorMsg.className = "text-muted small mb-0";
      noFlavorMsg.textContent = "No significant flavor profile data";
      container.appendChild(noFlavorMsg);
    }
  });

  // Initialize progress bars
  document.querySelectorAll(".progress-bar").forEach((bar) => {
    const width = bar.getAttribute("data-width");
    if (width) {
      bar.style.width = width + "%";
    }
  });
});
