document.addEventListener("DOMContentLoaded", function () {
  loadUsers();

  // ✅ Prevent auto-opening edit modal on login
  const params = new URLSearchParams(window.location.search);
  if (params.has("edit")) {
    toggleModal("editUserModal", false);
  }
});

// Toggle Modals
function toggleModal(modalId, show = true) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = show ? "block" : "none";
}

// Close QR Code Modal
function closeQrModal() {
  toggleModal("qrCodeModal", false);
  loadUsers();
}

// Open Add User Modal
function addUser() {
  toggleModal("addUserModal", true);
}

// Handle "Next" button click in Add User Modal
async function submitUserForm() {
  const username = document.getElementById("newUsername").value.trim();
  const email = document.getElementById("newEmail").value.trim();
  const password = document.getElementById("newPassword").value.trim();
  const role = document.getElementById("newRole").value.trim();

  if (!username || !email || !password || !role) {
    alert("Please fill in all fields.");
    return;
  }

  fetch("/admin/add_user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username,
      email: email,
      password: password,
      role: role,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Server response:", data); // Log response in console
      if (data.success) {
        alert("User added successfully!");
        location.reload();
      } else {
        console.error("Error:", data.error);
        alert("Error: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
      alert("An unexpected error occurred. Check the console for details.");
    });
}

// Email Validation Function
function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Close modals when clicking outside
window.onclick = function (event) {
  if (event.target.id === "addUserModal") toggleModal("addUserModal", false);
  if (event.target.id === "qrCodeModal") toggleModal("qrCodeModal", false);
};

// Function to switch sections
function showSection(section) {
  const sections = ["dashboard", "users", "documents", "analytics", "settings"];
  sections.forEach(
    (sec) => (document.getElementById(`${sec}-section`).style.display = "none")
  );
  document.getElementById(`${section}-section`).style.display = "block";
  document.getElementById("page-title").textContent =
    section.charAt(0).toUpperCase() + section.slice(1);
}

// Load users from the API
async function loadUsers() {
  try {
    const response = await fetch("/admin/get_users");
    if (!response.ok) throw new Error("Failed to fetch users");

    const users = await response.json();
    const userList = document.getElementById("user-list");
    userList.innerHTML = "";

    users.forEach((user) => {
      const row = `<tr>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.role}</td>
                    <td>
                        <button onclick="editUser(${user.id})">Edit</button>
                        <button onclick="deleteUser(${user.id})">Delete</button>
                    </td>
                  </tr>`;
      userList.innerHTML += row;
    });
  } catch (error) {
    console.error("Error loading users:", error);
  }
}

// Search Users
function searchUsers() {
  const input = document.getElementById("searchUser").value.toLowerCase();
  document.querySelectorAll("#user-list tr").forEach((row) => {
    const username = row.cells[0].textContent.toLowerCase();
    const email = row.cells[1].textContent.toLowerCase();
    row.style.display =
      username.includes(input) || email.includes(input) ? "" : "none";
  });
}

// Function to edit user
//function editUser(userId) {
//  window.location.href = `/auth/edit-user/${userId}`;
//}

// Fetch user details and populate the edit modal
async function editUser(userId) {
  if (!userId) return;
  try {
    const response = await fetch(`/admin/edit-user/${userId}`);
    if (!response.ok) throw new Error("Failed to fetch user details");

    const user = await response.json();

    // ✅ Populate form fields
    document.getElementById("editUserId").value = user.id;
    document.getElementById("editUsername").value = user.username;
    document.getElementById("editEmail").value = user.email;
    document.getElementById("editRole").value = user.role;

    // ✅ Handle QR Code Display
    const qrImage = document.getElementById("qrImage");
    const qrCodeSection = document.getElementById("qrCodeSection");

    if (user.qr_code && user.qr_code.trim() !== "") {
      qrImage.src = user.qr_code; // Set QR Code image
      qrCodeSection.style.display = "block"; // Show QR Code
    } else {
      qrCodeSection.style.display = "none"; // Hide QR Code if not available
    }

    // ✅ Open the modal
    toggleModal("editUserModal", true);
  } catch (error) {
    console.error("Error loading user details:", error);
    alert("Failed to load user details.");
  }
}

// Submit edited user data
async function submitEditUserForm() {
  const userId = document.getElementById("editUserId").value;
  const username = document.getElementById("editUsername").value.trim();
  const email = document.getElementById("editEmail").value.trim();
  const role = document.getElementById("editRole").value.trim();

  if (!username || !email || !role) {
    alert("Please fill in all fields.");
    return;
  }

  try {
    const response = await fetch(`/admin/edit-user/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, role }),
    });

    const data = await response.json();

    if (data.success) {
      alert("User updated successfully!");

      // ✅ Update QR Code dynamically
      if (data.qr_code) {
        document.getElementById("qrImage").src = data.qr_code;
        document.getElementById("qrCodeSection").style.display = "block";
      } else {
        document.getElementById("qrCodeSection").style.display = "none";
      }

      toggleModal("editUserModal", false);
      loadUsers();
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    console.error("Error updating user:", error);
    alert("An unexpected error occurred.");
  }
}

// Toggle modal visibility
function toggleModal(modalId, show) {
  document.getElementById(modalId).style.display = show ? "block" : "none";
}

// Close modal when clicking outside
window.onclick = function (event) {
  if (event.target.id === "editUserModal") toggleModal("editUserModal", false);
};

// Function to delete user
async function deleteUser(userId) {
  if (confirm("Are you sure you want to delete this user?")) {
    try {
      const response = await fetch(`/admin/delete_user/${userId}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error("Failed to delete user");

      alert("User deleted successfully!");
      loadUsers();
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  }
}
