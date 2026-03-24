document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: 'no-cache' });
      const activities = await response.json();
      console.log("[fetchActivities] activities loaded", activities);

      const participantsCards = document.getElementById("participants-cards");
      console.log("[fetchActivities] participantsCards element found?", participantsCards !== null, "element:", participantsCards);

      // Clear loading message and the activity selector so we avoid duplicate options
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = `<option value="">-- Select an activity --</option>`;
      participantsCards.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantItems = details.participants.length
          ? details.participants
              .map(
                (participant) =>
                  `<li class="participant-item"><span class="participant-name">${participant}</span><button class="delete-participant" data-activity="${name}" data-email="${participant}" title="Remove participant">✕</button></li>`
              )
              .join("")
          : "<li><em>No participants yet</em></li>";

        const participantsText = details.participants.length
          ? details.participants.join(", ")
          : "No participants yet";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <p class="participants-count"><strong>${details.participants.length}</strong> participant(s) registered</p>
          <p><strong>Member list:</strong> ${participantsText}</p>
          <div class="participants-section">
            <p><strong>Participants</strong></p>
            <ul class="participants-list">
              ${participantItems}
            </ul>
          </div>
        `;

        // Add delete handlers for each participant
        activityCard.querySelectorAll(".delete-participant").forEach((button) => {
          button.addEventListener("click", async () => {
            const activityName = button.dataset.activity;
            const email = button.dataset.email;

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
                {
                  method: "DELETE",
                }
              );
              const result = await response.json();

              if (response.ok) {
                messageDiv.textContent = result.message;
                messageDiv.className = "success";
                await fetchActivities();
              } else {
                messageDiv.textContent = result.detail || "Failed to remove participant";
                messageDiv.className = "error";
              }
              messageDiv.classList.remove("hidden");
              setTimeout(() => messageDiv.classList.add("hidden"), 5000);
            } catch (error) {
              messageDiv.textContent = "Failed to remove participant. Please try again.";
              messageDiv.className = "error";
              messageDiv.classList.remove("hidden");
              console.error("Error removing participant:", error);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        console.log(`[activity card] ${name} participants`, details.participants);

        // Build participant summary cards for the separate participants section
        if (!participantsCards) {
          console.warn("[participantSummaryCard] participantsCards element is null, skipping card append");
        } else {
          const participantSummaryCard = document.createElement("div");
          participantSummaryCard.className = "activity-participant-card";
          participantSummaryCard.innerHTML = `
            <h4>${name}</h4>
            <p class="participant-count">${details.participants.length} participant(s)</p>
            <div class="participant-badges">
              ${
                details.participants.length
                  ? details.participants.map((participant) => `<span class="participant-badge">${participant}</span>`).join("")
                  : "<span class=\"participant-empty\">No participants yet</span>"
              }
            </div>
          `;
          participantsCards.appendChild(participantSummaryCard);
          console.log(`[participantSummaryCard] appended for ${name}`);
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh the activity cards to show the updated participants list
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
