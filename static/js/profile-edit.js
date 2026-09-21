function ready() {
/**
 * This enables the profile page form for editing
 * Edit profile button is hidden
 * update profile button is made visible
 */
    function formEnable() {
        document.getElementById("fieldsetProfile").removeAttribute("disabled");
        document.getElementById("editProfileBtn").classList.add("visually-hidden");
        document.getElementById("updateProfileBtn").classList.remove("visually-hidden");
    }
    // this event listener is on the Edit your contact details
    document.getElementById("editProfileBtn").addEventListener("click", formEnable);
}

/**
 * This waits for document to be fully loaded
 * then runs the ready() function when loading is completed
 */
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready());
} else {
    ready();
}