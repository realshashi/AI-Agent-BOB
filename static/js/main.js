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
    let flavorData;
    try {
      // Try to parse the flavor data, with better error handling
      const rawData = container.getAttribute("data-flavors");
      console.log("Raw flavor data:", rawData); // Debug log
      flavorData = JSON.parse(rawData || "{}");
    } catch (e) {
      console.error("Error parsing flavor data:", e);
      flavorData = {};
    }

    // Clear any existing content
    container.innerHTML = "";

    // Debug log
    console.log("Parsed flavor data:", flavorData);

    // Create tag-based flavor profile visualization
    for (const [flavor, value] of Object.entries(flavorData)) {
      const numValue = Number(value);
      if (numValue > 0) {
        // Skip values that are too low to be meaningful
        if (numValue < 10) continue;

        const flavorTag = document.createElement("span");
        flavorTag.className = "flavor-tag";

        // Determine level based on value
        let level = "low";
        if (numValue > 70) {
          level = "high";
        } else if (numValue > 35) {
          level = "medium";
        }

        flavorTag.setAttribute("data-level", level);
        flavorTag.textContent =
          flavor.charAt(0).toUpperCase() + flavor.slice(1);
        flavorTag.title = `${flavor}: ${Math.round(numValue)}%`;
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

  // Handle progress bars
  document.querySelectorAll(".progress-bar").forEach((bar) => {
    const width = bar.getAttribute("data-width");
    if (width) {
      bar.style.width = width + "%";
    }
  });
});
