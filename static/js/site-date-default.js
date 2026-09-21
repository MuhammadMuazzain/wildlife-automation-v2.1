/**
 * Defaults application date fields to today and caps past-dated pickers where needed.
 */
function formatDate(date) {
    var d = new Date(date),
        month = "" + (d.getMonth() + 1),
        day = "" + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = "0" + month;
    if (day.length < 2) day = "0" + day;

    return [year, month, day].join("-");
}

var today = formatDate(new Date());
var applicationDate = document.getElementById("application_date");
if (applicationDate) {
    applicationDate.value = today;
    applicationDate.max = today;
}
