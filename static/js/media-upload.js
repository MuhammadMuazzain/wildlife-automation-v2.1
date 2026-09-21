var cloudName = window.PLOTDESK_CLOUDINARY_CLOUD || "";
var uploadPreset = window.PLOTDESK_CLOUDINARY_PRESET || "";

if (cloudName && uploadPreset && document.getElementById("upload_widget")) {
  var myWidget = cloudinary.createUploadWidget(
    {
      cloudName: cloudName,
      uploadPreset: uploadPreset,
      folder: "plotdesk",
    },
    function (error, result) {
      if (!error && result && result.event === "success") {
        document.getElementById("image").value = result.info.url;
        document.getElementById("img-thumbnail").src = result.info.url;
      }
    }
  );

  document.getElementById("upload_widget").addEventListener(
    "click",
    function () {
      myWidget.open();
    },
    false
  );
}
