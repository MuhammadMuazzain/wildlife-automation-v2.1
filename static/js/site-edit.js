function ready() {
    function formEnable() {
        document.getElementById("fieldset1").removeAttribute("disabled");
        document.getElementById("fieldset2").removeAttribute("disabled");
        document.getElementById("editSiteBtn").classList.add("visually-hidden");
        document.getElementById("saveSiteBtn").classList.remove("visually-hidden");
        document.getElementById("deleteSiteBtn").classList.remove("visually-hidden");
        var upload = document.getElementById("upload_widget");
        if (upload) {
            upload.classList.remove("visually-hidden");
        }
        document.getElementById("heading-site-view-page").innerText = "Edit garden plot";
    }

    var editBtn = document.getElementById("editSiteBtn");
    if (editBtn) {
        editBtn.addEventListener("click", formEnable);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
} else {
    ready();
}
